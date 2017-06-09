#pragma once
class Battle
{
public:
	Battle();
	bool isActive();
	void update();
	bool operator == (Battle const& autre) const {
		return this==&autre; }
private:
	bool m_actif;
};

