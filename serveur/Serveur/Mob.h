#ifndef MOB_H_INCLUDED
#define MOB_H_INCLUDED

#include "Entitee.h"
#include "TypeMob.h"
#include <iostream>

class Mob : public Entitee
{
public:
    Mob();
    Mob(TypeMob type,int level);
	virtual void mort();
	void afficher() const;
};


#endif // MOB_H_INCLUDED
