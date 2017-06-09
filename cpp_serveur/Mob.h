#pragma once

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
