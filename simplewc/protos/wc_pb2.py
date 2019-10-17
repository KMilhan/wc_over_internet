# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: wc.proto

import sys

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode("latin1"))

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
    name="wc.proto",
    package="",
    syntax="proto3",
    serialized_options=None,
    serialized_pb=_b(
        '\n\x08wc.proto".\n\x10WordCountRequest\x12\x0b\n\x03uri\x18\x01 \x01(\t\x12\r\n\x05words\x18\x02 \x03(\t"5\n\tWordCount\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\x0b\n\x03uri\x18\x02 \x01(\t\x12\r\n\x05\x63ount\x18\x03 \x01(\r2m\n\x10WordCountService\x12-\n\nCountWords\x12\x11.WordCountRequest\x1a\n.WordCount0\x01\x12*\n\tCountWord\x12\x11.WordCountRequest\x1a\n.WordCountb\x06proto3'
    ),
)

_WORDCOUNTREQUEST = _descriptor.Descriptor(
    name="WordCountRequest",
    full_name="WordCountRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="uri",
            full_name="WordCountRequest.uri",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="words",
            full_name="WordCountRequest.words",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=12,
    serialized_end=58,
)

_WORDCOUNT = _descriptor.Descriptor(
    name="WordCount",
    full_name="WordCount",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="word",
            full_name="WordCount.word",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="uri",
            full_name="WordCount.uri",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="count",
            full_name="WordCount.count",
            index=2,
            number=3,
            type=13,
            cpp_type=3,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=60,
    serialized_end=113,
)

DESCRIPTOR.message_types_by_name["WordCountRequest"] = _WORDCOUNTREQUEST
DESCRIPTOR.message_types_by_name["WordCount"] = _WORDCOUNT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

WordCountRequest = _reflection.GeneratedProtocolMessageType(
    "WordCountRequest",
    (_message.Message,),
    dict(
        DESCRIPTOR=_WORDCOUNTREQUEST,
        __module__="wc_pb2"
        # @@protoc_insertion_point(class_scope:WordCountRequest)
    ),
)
_sym_db.RegisterMessage(WordCountRequest)

WordCount = _reflection.GeneratedProtocolMessageType(
    "WordCount",
    (_message.Message,),
    dict(
        DESCRIPTOR=_WORDCOUNT,
        __module__="wc_pb2"
        # @@protoc_insertion_point(class_scope:WordCount)
    ),
)
_sym_db.RegisterMessage(WordCount)

_WORDCOUNTSERVICE = _descriptor.ServiceDescriptor(
    name="WordCountService",
    full_name="WordCountService",
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    serialized_start=115,
    serialized_end=224,
    methods=[
        _descriptor.MethodDescriptor(
            name="CountWords",
            full_name="WordCountService.CountWords",
            index=0,
            containing_service=None,
            input_type=_WORDCOUNTREQUEST,
            output_type=_WORDCOUNT,
            serialized_options=None,
        ),
        _descriptor.MethodDescriptor(
            name="CountWord",
            full_name="WordCountService.CountWord",
            index=1,
            containing_service=None,
            input_type=_WORDCOUNTREQUEST,
            output_type=_WORDCOUNT,
            serialized_options=None,
        ),
    ],
)
_sym_db.RegisterServiceDescriptor(_WORDCOUNTSERVICE)

DESCRIPTOR.services_by_name["WordCountService"] = _WORDCOUNTSERVICE

# @@protoc_insertion_point(module_scope)
