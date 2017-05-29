#ifndef EFFET_H_INCLUDED
#define EFFET_H_INCLUDED

enum Effets
{
	vie
};

class Effet
{
public:
	Effet();
	Effet(Effets s_type,int s_duree, int s_puissance);
	const Effets type;
	int duree;
	const int puissance;
	bool operator== (Effet const& autre) const { return (type==autre.type) && (duree==autre.duree) && (puissance==autre.puissance); }
};

#endif
