\ Model MWIS
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x[0] + x[1] + x[2] + x[3] + x[4] + x[5]
Subject To
 R0: x[0] + x[1] <= 1
 R1: x[0] + x[3] <= 1
 R2: x[1] + x[5] <= 1
 R3: x[2] + x[3] <= 1
 R4: x[2] + x[4] <= 1
 R5: x[4] + x[5] <= 1
Bounds
Binaries
 x[0] x[1] x[2] x[3] x[4] x[5]
End
