"""This is example program using WordCount gRPC service"""
from typing import Iterable

import grpc

from simplewc.config import INSECURE_HOST, INSECURE_PORT
from simplewc.protos.wc_pb2 import WordCountRequest, WordCount
from simplewc.protos.wc_pb2_grpc import WordCountServiceStub


def print_responses(responses: Iterable[WordCount]):
    """Print the stream of response"""
    responses = list(responses)
    if not responses:
        print('\tNo word found')
    for r in responses:
        print(f'\tAt {r.uri}, word {r.word} appears {r.count} time(s)')


def run():
    """Run Example Program"""
    channel = grpc.insecure_channel(f'{INSECURE_HOST}:{INSECURE_PORT}')
    stub = WordCountServiceStub(channel)
    responses = stub.CountWords(WordCountRequest(
        uri='https://virtusize.jp', words=['fit', 'size', 'virtusize']))
    print('Try to find 3 different words in a URL')
    print_responses(responses)

    print('\n\nTry to find nothing')
    responses = stub.CountWords(WordCountRequest(uri='https://virtusize.jp',
                                                 words=[]))
    print_responses(responses)

    print('\n\nInaccessible host: non existing https://virtusize.co.jp')
    try:
        responses = stub.CountWords(WordCountRequest(
            uri='https://virtusize.co.jp', words=[]))
        list(responses)
    except grpc.RpcError as e:
        print('\tRPC Error', e)

    print('\n\nInaccessible host: 127.0.0.1')
    try:
        responses = stub.CountWords(WordCountRequest(
            uri='https://127.0.0.1', words=[]))
        list(responses)
    except grpc.RpcError as e:
        print('\tRPC Error', e)

    print('\n\nInaccessible host: file:///etc/apt/sources.list')
    try:
        responses = stub.CountWords(WordCountRequest(
            uri='file:///etc/apt/sources.list', words=['round']))
        list(responses)
    except grpc.RpcError as e:
        print('\tRPC Error', e)


if __name__ == '__main__':
    run()
