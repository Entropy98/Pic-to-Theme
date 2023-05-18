from typing import NewType, List

AnsiColor = NewType("AnsiColor", str)
ColorString = NewType("ColorString", str)
HexColor = NewType("HexColor", int)

ColorList = NewType("ColorList", List[HexColor])
Img = NewType("Img", List[List[int]])
ImgPath = NewType("ImgPath", str)
RGBVal = NewType("RGBVal", List[int])
