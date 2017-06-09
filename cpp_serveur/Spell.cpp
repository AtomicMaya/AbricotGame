#include "Spell.h"

Spell::Spell() : m_name(""),m_cost(0),m_reload(0) {}

void Spell::appliquer_effet(Entitee &cible)const
{
	for each(Effet i in m_effect)
	{
		cible.recevoir_effet(i);
	}
}
