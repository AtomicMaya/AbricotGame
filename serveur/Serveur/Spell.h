#ifndef SPELL_H_INCLUDED
#define SPELL_H_INCLUDED

#include <string>
#include <vector>
#include "Entitee.h"

class Spell
{
public:
	Spell();
	virtual bool verif_condition() const = 0;
	void appliquer_effet(Entitee &cible) const;
	virtual void liste_cases() const = 0;
private:
	const std::string m_name;
	const int m_cost;
	const int m_reload;
	std::vector<Effet> m_effect;
};

#endif
