#ifndef ENTITEE_H_INCLUDED
#define ENTITEE_H_INCLUDED
#include "Coordinates.h"
#include "Caracteristiques.h"

class Entitee
{
public:
    Entitee();
    Entitee(int vie, int energie, int vitesse);
private:
    Coordinates m_position;
    Caracteristiques m_maxAttributs;
    Caracteristiques m_varAttributs;
};

#endif // ENTITEE_H_INCLUDED
