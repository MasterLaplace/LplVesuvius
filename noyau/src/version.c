/* version.c -- ce que le noyau dit de lui-même. */
#include "vesuve.h"

const char *vesuve_version(void) { return VESUVE_VERSION; }

const char *vesuve_nom_du_statut(vesuve_statut statut)
{
    switch (statut) {
    case VESUVE_OK: return "ok";
    case VESUVE_ARGUMENT: return "argument hors domaine";
    case VESUVE_INDECIDABLE: return "indécidable";
    case VESUVE_NON_IMPLEMENTE: return "non implémenté (V-001)";
    }
    return "statut inconnu";
}
