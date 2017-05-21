#ifndef ENTITEE_H_INCLUDED
#define ENTITEE_H_INCLUDED
#include "Coordinates.h"
#include "Caracteristiques.h"
#include "Effet.h"
#include <list>
#include <string>

class Entitee
{
public:
    Entitee();
    Entitee(int vie, int energie, int vitesse);
	void recevoir_effet(Effet effet);
private:
	void subir_effet(Effet & effet);
	std::string name;
    Coordinates m_position;
    Caracteristiques m_maxAttributs;
    Caracteristiques m_varAttributs;
	std::list<Effet> m_effetsSubis;
	virtual void mort()=0;
};

#endif // ENTITEE_H_INCLUDED
