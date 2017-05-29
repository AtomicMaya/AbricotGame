#ifndef CARACTERISTIQUES_H_INCLUDED
#define CARACTERISTIQUES_H_INCLUDED
class Caracteristiques
{
public:
    int vie;
    int energie;
    int vitesse;
    Caracteristiques();
    Caracteristiques(int s_vie,int s_energie, int s_vitesse);
    Caracteristiques operator+ (Caracteristiques const& rhs) const
    {
        return Caracteristiques(vie + rhs.vie, energie + rhs.energie,vitesse + rhs.vitesse);
    }

    Caracteristiques operator- (Caracteristiques const& rhs) const
    {
        return Caracteristiques(vie - rhs.vie, energie - rhs.energie,vitesse - rhs.vitesse);
    }

    Caracteristiques operator* (int rhs) const
    {
        return Caracteristiques(vie * rhs, energie * rhs,vitesse * rhs);
    }
};

#endif // CARACTERISTIQUES_H_INCLUDED
