#pragma once

#include "Coordinates.h"
#include "Caracteristiques.h"
#include "Effet.h"
#include <list>
#include "Spell.h"
#include <vector>

class Spell;

class Entitee
{
public:
    Entitee();
    Entitee(int vie, int energie, int vitesse,std::string name,int level,const std::vector<Spell*> &spells);
    Entitee(Caracteristiques max,std::string name,int level,const std::vector<Spell*> &spells);
	void recevoir_effet(Effet effet);
protected:
	void subir_effet(Effet &effet);
	virtual void mort()=0;
	const std::string m_name;
    Coordinates m_position;
    Caracteristiques m_maxAttributs;
    Caracteristiques m_varAttributs;
	std::list<Effet> m_effetsSubis;
	const std::vector<Spell*> m_spells;
	int m_level;
};