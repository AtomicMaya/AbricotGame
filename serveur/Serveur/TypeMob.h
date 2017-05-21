#ifndef TYPEMOB_H_INCLUDED
#define TYPEMOB_H_INCLUDED

#include <string>
#include "Caracteristiques.h"

class TypeMob
{
public:
    TypeMob();
private:
    const std::string m_name;
    const Caracteristiques m_baseAttributs;
    const Caracteristiques m_xAttributs;
};

#endif // TYPEMOB_H_INCLUDED
