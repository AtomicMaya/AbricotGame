#include "Mob.h"

Mob::Mob() :Entitee() {}

Mob::Mob(TypeMob type, int level) : Entitee(type.getCaracteristiques(level), type.getName(), int(level), type.getSpells()) {}

void Mob::afficher() const
{
	std::cout << "nom : " << m_name << ", level : " << m_level << ", vie : " << m_varAttributs.vie << ", energie : " << m_varAttributs.energie << ", vitesse : " << m_varAttributs.vitesse << std::endl;
}

void Mob::mort()
{
	std::cout << m_name << " est mort." << std::endl;
}
