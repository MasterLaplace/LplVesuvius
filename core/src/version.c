/* version.c -- what the core says about itself. */
#include "vesuve.h"

const char *vesuve_version(void) { return VESUVE_VERSION; }

const char *vesuve_status_name(vesuve_status status)
{
    switch (status) {
    case VESUVE_OK: return "ok";
    case VESUVE_BAD_ARGUMENT: return "argument outside its domain";
    case VESUVE_UNDECIDABLE: return "undecidable";
    case VESUVE_NOT_IMPLEMENTED: return "not implemented";
    }
    return "unknown status";
}
