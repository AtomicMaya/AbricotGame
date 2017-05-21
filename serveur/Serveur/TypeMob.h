#ifndef TYPEMOB_H_INCLUDED
#define TYPEMOB_H_INCLUDED

#include <string>
#include "Caracteristiques.h"
#include <vector>
#include "Spell.h"

class TypeMob
{
public:
    TypeMob();
private:
    const std::string m_name;
    const Caracteristiques m_baseAttributs;
    const Caracteristiques m_xAttributs;
	const std::vector<Spell> sorts;
};

#endif // TYPEMOB_H_INCLUDED
