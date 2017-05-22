#include "Spell.h"

Spell::Spell() : m_name(""),m_cost(0),m_reload(0) {}

void Spell::appliquer_effet(Entitee &cible)const
{
	for (int i=0; i != m_effect.size(); ++i)
	{
		cible.recevoir_effet(m_effect[i]);
	}
}
