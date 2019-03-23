# WC Over Internet

## Introduction
Hierarchically cached word counter over the internet service, exposed as gRPC 
service.

This program access a specific location in the web and count a word in HTML 
document. Except,
    * when user asks internal resource like `file://etc/fstab` or `https://cluster.local`
    * when user asks too big page such as `https://download.ubuntu.org/installation_image.iso`
    * (check ```simplewc/simplewc/tests/test_security.py``` for more cases.)

Internally, this program reuses and caches many parts including most 
recent results, HTML documentation.
  * You can call the API on same HTML resource multiple times. It will 
  generate only one HTML documentation download from the target public web host
  in most cases.
  * Most recent accessed query and past retrieved HTML documents can have 
  separate data storages so you can have cheap storage as a documentation 
  storage and in-memory cache server as a request cache server

### Internal Structure Overview
1. Transport Layer
    - gRPC
1. Service Layer
    - gRPC servicer implementation using our model
1. Data Model Layer
    - class `HTMLDocument`
1. Data storage layer
    - Multiple databases

## How to use
Use gRPC service ```rpc CountWords (WordCountRequest) returns (stream 
WordCount)``` in your favorite language.
  * `CountWords` returns gRPC stream of `WordCount`
  * `WordCountRequest` contains one URI to the HTML document and word(s) to count
  * `WordCount` contains one URI, one word, and its appearance
  * Error code and messages are handled in gRPC standard error code

Example client script is provided in ```simplewc/simplewc/example_client.py```.

The simplest example would be,
```python
channel = grpc.insecure_channel(f'localhost:50051')
stub = WordCountServiceStub(channel)
response_stream = stub.CountWords(WordCountRequest(
    uri='https://virtusize.jp', words=['fit', 'size', 'virtusize']))
for r in response_stream:
    print(f'\tAt {r.uri}, word {r.word} appears {r.count} time(s)')
```

### API
API is provided in a form of gRPC `rpc`.
```proto
/* WordCountService services word counting based on WordCountRequest message.
 * * Note on caching:
 *     - The implementation of this service may contain internal caching on
 *       HTML document.
 *     - Request multiple word count in a single uri rather than calling
 *       any services multiple times. */
service WordCountService {
    /* Service each word's occurrence in a certain uri.
     * If error happens, it will cut a stream and send gRPC error code with
     * detailed message instead of WordCount stream */
    rpc CountWords (WordCountRequest) returns (stream WordCount);
}
```

### Message
messages are provided in a form of `protobuf` message. For the details, please 
refer to proto file at 
```simplewc/simplewc/protos/wc.proto```, which looks like ...
```proto
/* WordCountRequest represents a word count query. You can specify multiple
 *  words at the same time */
message WordCountRequest {
    string uri = 1;
    repeated string words = 2;
}

/* WordCount represents a word and a occurrence of it in uri */
message WordCount {
    string word = 1;
    string uri = 2;
    uint32 count = 3;
}
```

The example client runs as follows:
    ```text
    Try to find 3 different words in a URL
        At https://virtusize.jp, word fit appears 4 time(s)
        At https://virtusize.jp, word size appears 0 time(s)
        At https://virtusize.jp, word virtusize appears 4 time(s)
    
    
    Try to find nothing
        No word found
    
    
    Inaccessible host: non existing https://virtusize.co.jp
        RPC Error <_Rendezvous of RPC that terminated with:
        status = StatusCode.INTERNAL
        details = "We could not reach a server of requested URI"
        debug_error_string = "{"created":"@1553340540.602000000","description":"Error received from peer","file":"src/core/lib/surface/call.cc","file_line":1039,"grpc_message":"We could not reach a server of requested URI","grpc_status":13}"
    >
    
    
    Inaccessible host: 127.0.0.1
        RPC Error <_Rendezvous of RPC that terminated with:
        status = StatusCode.PERMISSION_DENIED
        details = "You cannot access Local URI"
        debug_error_string = "{"created":"@1553340540.603000000","description":"Error received from peer","file":"src/core/lib/surface/call.cc","file_line":1039,"grpc_message":"You cannot access Local URI","grpc_status":7}"
    >
    
    
    Inaccessible host: file:///etc/apt/sources.list
        RPC Error <_Rendezvous of RPC that terminated with:
        status = StatusCode.PERMISSION_DENIED
        details = "You can only access ('http', 'https') protocol"
        debug_error_string = "{"created":"@1553340540.604000000","description":"Error received from peer","file":"src/core/lib/surface/call.cc","file_line":1039,"grpc_message":"You can only access ('http', 'https') protocol","grpc_status":7}"
    >
    
    ```
## How it works
1. User send a request, (uri, multiple words)
1. Check if it's safe request
1. Open a stream
1. In every word,
    - Check if a (uri/word) combination is in result cache
        * Do not update TTL of cache. Return the result
    - If not, check local memory if we already loaded a HTML document.
        * If we have a document in local memory, return the result and update 
          query cache
        * If not, check document storage in local network,
            - If we have a document in a storage, update recent query cache and 
              return the result
            - If we don't even have it, get it over the internet
                * Store both HTML document and recent result
1. Close a stream if,
    - Met the last result
    - Found an error
        * Send error code and detailed message
  
## How to deploy
Use ```simplewc.servicer:serve_insecure```. For the configuration, refer to 
```simplewc.config```.

## How to build proto
Prepare `grpc_tools` and `mypy-protobuf` on your dev environment, then
```bash
> python -m grpc_tools.protoc -Isimplewc/simplewc/protos --python_out=simplewc/simplewc/protos --grpc_python_out=simplewc/simplewc/
protos --mypy_out=simplewc/simplewc/protos  wc.proto
```
, on Windows, add 
```bash
--plugin=protoc-gen-mypy=path\to\mypy-protobuf\python\protoc_gen_mypy.bat 
```

## Limitations
1. If encoding is not specified in HTML, this only works with UTF-8 encoded 
pages.
    - We can improve with encoding guessing. There are good oss 
      implementations such as `cchardet`
1. User can find a word maximum length of 4MB

## Design choices
1. Web page cache
    - Counting all the words and one word takes same time complexity, O(n).
        * So we save all word count of a document
      - Average HTML document size is ~ [30KB](https://www.igvita.com/2016/01/12/the-average-page-is-a-myth/)
        * Google expects [60 Billions](https://www.worldwidewebsize.com/) web page exist
            - We can cache 0.00005% of web pages per 1 GB.
                * We can store 1% of web pages only with 20TB storage
                * But we are not building Google scale API here.
                * Or, we can store ~ 2 Million web pages for 64GB of storage
            - it takes ~60 seconds to fill up 64 GB storage with 10G internet 
              connection, w/o any overhead.
                * But, HTML document size may vary greatly by each web pages, thus 
                  let's create a strategy to expire data to maintain 50% 
                  usage of disk 
                * Minimum lifetime of each cache record will be (*storage size*)/
                  (*internet speed*)
                    - NOTE: (bytes) / (bytes/time) = time
                * Maximum lifetime of each cache record must be set by the user
                * To maintain the cache size ~ *storage size*/2,
                    - as (*v_create* - *v_expire*) * *dt* = *delta_storage*, we
                  can solve ODE
                    - or in a very rough approximation, we can use (*(1-t)* *max* - *t* 
                      *min*), where *t* = min(*current storage usage* / 
                     (*storage size*/2), 1)

1. Query result cache
    - Each record will take ~ 4KB (1KB of URL, 1KB of word, 4bytes of count + 
      overhead)
        * We can save ~4 millions of query result in 16GB memory.
        * We can set the TTL of cache, and keep them in LRU fashion.

1. Choice of Database Solution
    - Web page cache
        - Cheap storage(disk-based), TTL supported, document database: MongoDB
    - Query result cache
        - In-memory, fast membership check, LRU support: Redis
    
