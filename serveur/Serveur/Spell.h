#ifndef SPELL_H_INCLUDED
#define SPELL_H_INCLUDED

#include <string>
#include <map>

class Spell
{
public:
	Spell();
	virtual bool verif_condition() const = 0;
	void appliquer_effet() const;
	virtual void liste_cases() const = 0;
private:
	const std::string m_name;
	const int m_cost;
	const int m_reload;
	const std::map<int, int> effect;
};

#endif
