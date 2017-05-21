#include "Entitee.h"

Entitee::Entitee(int vie, int energie, int vitesse):m_position(-1,-1),
    m_maxAttributs(vie,energie,vitesse),
    m_varAttributs(vie,energie,vitesse) {}

Entitee::Entitee():m_position(-1,-1),m_maxAttributs(-1,-1,-1),m_varAttributs(-1,-1,-1) {}
