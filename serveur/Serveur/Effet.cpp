#include "Effet.h"

Effet::Effet():duree(0),puissance(0),type(vie)
{

}

Effet::Effet(Effets s_type, int s_duree, int s_puissance):type(s_type),puissance(s_puissance),duree(s_duree)
{

}