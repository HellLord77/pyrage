# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
from .File import File
from typing import Optional
np = import_numpy()

class Files(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Files()
        x.Init(buf, n + offset)
        return x

    # Files
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Files
    def Files(self, j: int) -> Optional[File]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            obj = File()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # Files
    def FilesLength(self) -> int:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Files
    def FilesIsNone(self) -> bool:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

def Start(builder: flatbuffers.Builder):
    builder.StartObject(1)

def AddFiles(builder: flatbuffers.Builder, files: int):
    builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(files), 0)

def StartFilesVector(builder, numElems: int) -> int:
    return builder.StartVector(4, numElems, 4)

def End(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()

