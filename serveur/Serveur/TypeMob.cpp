#include "TypeMob.h"

TypeMob::TypeMob() :m_name(""), m_baseAttributs(0, 0, 0), m_xAttributs(0, 0, 0) {}

TypeMob::TypeMob(std::string name, Caracteristiques baseAttributs, Caracteristiques xAttributs, std::vector<Spell*> sorts) :
	m_name(name), m_baseAttributs(baseAttributs), m_xAttributs(xAttributs), m_sorts(sorts) {}

std::string TypeMob::getName()
{
	return m_name;
}

Caracteristiques TypeMob::getCaracteristiques(int level)
{
	return Caracteristiques(m_baseAttributs.vie + m_xAttributs.vie*level, m_baseAttributs.energie + m_xAttributs.energie*level, m_baseAttributs.vitesse + m_xAttributs.vitesse*level);
}

const std::vector<Spell*>& TypeMob::getSpells()
{
	return m_sorts;
}
