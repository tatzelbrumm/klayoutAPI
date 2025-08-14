| Location                        | Purpose                                                                                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **`$HOME/.klayout/libraries/`** | User-local libraries. Any file here (`.gds`, `.oas`, `.lym`, `.lyp`, `.lym`+`.gds` combo) is considered a library.                        |
| **`$KLAYOUT_HOME/libraries/`**  | Same as above but under a different base if you set `KLAYOUT_HOME`.                                                                       |
| **`$KLAYOUT_LIBRARY_PATH`**     | Extra colon- or semicolon-separated directories you tell it to search (not set by default).                                               |
| **Tech packages’ `libraries/`** | If you have an installed technology (e.g., `~/.klayout/tech/IHP130/`), KLayout scans its `libraries/` subfolder when that tech is active. |
| **Built-in / system dirs**      | Where system-wide KLayout installs may have preloaded libs (rare for most users).                                                         |

