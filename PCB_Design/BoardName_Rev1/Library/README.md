# README

### Generate Symbol & Footprint with JLC2KiCAD

- From the project root directory, open a terminal and run the following command.

  ```bash
  JLC2KiCadLib LCSC_PART_NUMBER -dir Library -footprint_lib BoardName.pretty
  ```

- The command will add the footprint directly to the `BoardName.pretty` library.
- The symbol has to be added manually using Kicad. Open the Project Symbol Library using Kicad symbol editor, add the new symbol from the `Library/symbol` directory.
- This will add the symbol to the project symbol library (`BoardName.kicad_sym`).
