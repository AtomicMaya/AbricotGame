#include "Entitee.h"

Entitee::Entitee(int vie, int energie, int vitesse) :m_position(-1, -1),
m_maxAttributs(vie, energie, vitesse),
m_varAttributs(vie, energie, vitesse) {}

Entitee::Entitee() : m_position(-1, -1), m_maxAttributs(-1, -1, -1), m_varAttributs(-1, -1, -1) {}

void Entitee::subir_effet(Effet & effet)
{
	if (effet.duree>0)
	{
		effet.duree--;
		switch (effet.type)
		{
		case vie:
			m_varAttributs.vie += effet.puissance;
			if (m_varAttributs.vie<1)
			{
				mort();
			}
			else if (m_varAttributs.vie>m_maxAttributs.vie)
			{
				m_varAttributs.vie = m_maxAttributs.vie;
			}

			break;
		}
	}
	else
	{
		m_effetsSubis.remove(effet);
	}

}

void Entitee::recevoir_effet(Effet effet)
{
	m_effetsSubis.push_back(effet);
	subir_effet(effet);
}