COMOX = "comox little river"
POWELL_RIVER = "powell river westview"
GALIANO_ISLAND = "galiano island sturdies bay"
VANCOUVER_TSAWWASSEN = "vancouver tsawwassen"
VANCOUVER_HORSESHOE_BAY = "vancouver horseshoe bay"
NANAIMO_DEPARTURE_BAY = "nanaimo departure bay"
LANGDALE = "sunshine coast langdale"
VICTORIA = "victoria swartz bay"
NANAIMO_DUKE_POINT = "nanaimo duke point"
PENDER_ISLAND = "pender island otter bay"
MAYNE_ISLAND = "mayne island village bay"
SATURNA_ISLAND = "saturna island lyall harbour"
SALT_SPRING_ISLAND "salt spring island long harbour"

terminal_map = {
  COMOX: [
    POWELL_RIVER
  ],
  GALIANO_ISLAND: [
    VANCOUVER_TSAWWASSEN
  ],
  VANCOUVER_HORSESHOE_BAY: [
    NANAIMO_DEPARTURE_BAY,
    LANGDALE,
  ],
  MAYNE_ISLAND: [
    VANCOUVER_TSAWWASSEN
  ],
  NANAIMO_DEPARTURE_BAY: [
    VANCOUVER_HORSESHOE_BAY
  ],
  NANAIMO_DUKE_POINT: [
    VANCOUVER_TSAWWASSEN
  ],
  PENDER_ISLAND: [
    VANCOUVER_TSAWWASSEN
  ],
  POWELL_RIVER: [
    COMOX
  ],
  SALT_SPRING_ISLAND: [
    VANCOUVER_TSAWWASSEN
  ],
  SATURNA_ISLAND: [
    VANCOUVER_TSAWWASSEN
  ],
  LANGDALE: [
    VANCOUVER_HORSESHOE_BAY
  ],
  VANCOUVER_TSAWWASSEN: [
    VICTORIA,
    NANAIMO_DUKE_POINT,
    PENDER_ISLAND,
    GALIANO_ISLAND,
    MAYNE_ISLAND,
    SATURNA_ISLAND,
    SALT_SPRING_ISLAND
  ],
  VICTORIA: [
    VANCOUVER_TSAWWASSEN
  ]
}
