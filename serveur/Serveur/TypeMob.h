#ifndef TYPEMOB_H_INCLUDED
#define TYPEMOB_H_INCLUDED

#include <string>
#include "Caracteristiques.h"
#include "Spell.h"

class TypeMob
{
public:
    TypeMob();
	TypeMob(std::string name,Caracteristiques baseAttributs,Caracteristiques xAttributs, std::vector<Spell*> sorts);
    std::string getName();
    Caracteristiques getCaracteristiques(int level);
    const std::vector<Spell*>& getSpells();

private:
    const std::string m_name;
    const Caracteristiques m_baseAttributs;
    const Caracteristiques m_xAttributs;
	const std::vector<Spell*> m_sorts;
};

#endif // TYPEMOB_H_INCLUDED
