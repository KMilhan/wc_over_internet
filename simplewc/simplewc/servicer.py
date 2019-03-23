import time
from concurrent import futures

import grpc

from simplewc import config
from simplewc import exceptions
from simplewc.model import HTMLDocumentModel
from simplewc.protos import wc_pb2_grpc
from simplewc.protos.wc_pb2 import WordCountRequest, WordCount
from simplewc.protos.wc_pb2_grpc import WordCountServiceServicer
from simplewc.storage import mds, mqc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class WordCountServicer(WordCountServiceServicer):
    """gRPC servicer for WordCountService"""

    def CountWords(self, request: WordCountRequest, context):
        """
        API for Word Count
        :param request: gRPC request of `WordCountRequest`
        :param context: gRPC context
        :return:
          * stream of `WordCount`. in a form of Generator
        :exception: cut stream, then `return` grpc error code and grpc error msg
        """
        try:
            uri, words = request.uri, request.words
            model = HTMLDocumentModel(uri, mds, mqc)
            for word in words:
                yield WordCount(uri=uri, word=word,
                                count=model.count_word(word))
            return

        except exceptions.NotAllowedScheme:
            msg = f'You can only access {config.ALLOWED_PROTOCOLS} protocol'
            context.set_details(msg)
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            return

        except exceptions.AccessLocalURI:
            msg = 'You cannot access Local URI'
            context.set_details(msg)
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            return

        except exceptions.TooBigResource:
            msg = f'You can only access less than' \
                f'{config.MAX_CONTENT_SIZE} bytes document'
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return

        except exceptions.NotReacheableLocation:
            msg = 'We could not reach a server of requested URI'
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)

        except Exception as e:
            msg = 'Internal error occurred'
            print(e)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            return


def serve_insecure(host_port: str):
    """Open Insecure service of `WordCountServicer`"""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.MAX_GRPC_SERVER_THREADS))
    wc_pb2_grpc.add_WordCountServiceServicer_to_server(WordCountServicer(),
                                                       server)
    server.add_insecure_port(host_port)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
