#include "Mob.h"
#include "Map.h"
#include "Battle.h"

void test()
{
	
	TypeMob patate("patate", Caracteristiques(200, 100, 3), Caracteristiques(20, 0, 0), std::vector<Spell*>());
	TypeMob abricot("abricot", Caracteristiques(100, 100, 3), Caracteristiques(10, 10, 0), std::vector<Spell*>());
	Mob mob1(patate, 5);
	mob1.afficher();
	Mob mob2(patate, 3);
	mob2.afficher();
	Mob mob3(abricot, 3);
	mob3.afficher();
	mob3.recevoir_effet(Effet(vie, 1, -10));
	mob3.afficher();
	mob3.recevoir_effet(Effet(vie, 1, 20));
	mob3.afficher();
	mob3.recevoir_effet(Effet(vie, 1, -150));
	mob3.afficher();
	system("PAUSE");
}

void boucle(std::vector<Map> &maps,std:: vector<Battle> &battles)
{
	for each (Map map in maps)
	{
		map.update();
	}
	for each (Battle battle in battles)
	{
		if (battle.isActive())
		{
			battle.update();
		}
		else
		{
			auto it = std::find(battles.begin(), battles.end(), battle);
			std::swap(*it, battles.back());
			battles.pop_back();
		}
	}
}

int main()
{
	test();
	bool serveurActif = true;
	std::vector<Map> maps = std::vector<Map>();
	std::vector<Battle>battles = std::vector<Battle>();
	while (serveurActif)
	{
		boucle(maps,battles);
	}
	return 0;
}
