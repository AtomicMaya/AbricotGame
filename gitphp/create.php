<<<<<<< HEAD
﻿<?php 
	class MyDB extends SQLite3
	{
		function __construct()
		{
			$this->open("players.db3");
		}
	}
	
	$db = new MyDB();
	if(!$db){
		echo "Erreur inconnue, veuillez réessayer plus tard.\n";
	} 
	/*
	$sql =<<<EOF
      CREATE TABLE PLAYERS
      (LOGIN           TEXT    NOT NULL,
      MDP            TEXT     NOT NULL,
      EMAIL        TEXT);
EOF;

	$ret = $db->exec($sql);
	if(!$ret){
		echo $db->lastErrorMsg();
	} else {
		echo "Records created successfully\n";
	}	*/

	$pseudo = $_POST["pseudo"];
	$mdp = $_POST["mdp"];
	$mdpC = $_POST["mdpC"];
	$email = $_POST["email"];
	
	if(get_magic_quotes_gpc()===1) 
	{ 
     $pseudo = stripslashes($pseudo); 
     $mdp = stripslashes($mdp); 
	 $mdpC = stripslashes($mdpC); 
	 $email = stripslashes($email);
	} 

	/** 
	* On protège les chaînes 
	*/ 

    $pseudo = $db->escapeString($pseudo); 
    $mdp = $db->escapeString($mdp); 
	$mdpC = $db->escapeString($mdpC); 
    $email = $db->escapeString($email); 
	$mdp = hash('sha512', $mdp);
	$mdpC = hash('sha512', $mdpC);
	if ($mdpC==$mdp)
	{
		 
		$sql = $db->prepare("SELECT :pseudo FROM PLAYERS WHERE LOGIN=:pseudo ;");
		$sql->bindValue(':pseudo', $pseudo);
		$ret = $sql->execute();

		$n = 0;
		while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
		  $n += 1;
		}
		//echo $n;
		
		if($n!=0){
			echo "Ce pseudo est déjà utilisé.";
		} else {
			$sql = $db->prepare("INSERT INTO PLAYERS (LOGIN, MDP, EMAIL) VALUES (:pseudo, :mdp, :email);");
			$sql->bindValue(':pseudo', $pseudo);
			$sql->bindValue(':mdp', $mdp);
			$sql->bindValue(':email', $email);

			$ret = $sql->execute();
			if(!$ret){
				echo "Erreur ic";
			} else {
				echo "Compte crée avec succès \n";
			}
		}
	} else{
		echo "Les mots de passe ne sont pas identiques.\n";
	}	
	$db->close();
	
?>
=======
﻿<?php 
	class MyDB extends SQLite3
	{
		function __construct()
		{
			$this->open("players.db3");
		}
	}
	
	$db = new MyDB();
	if(!$db){
		echo "Erreur inconnue, veuillez réessayer plus tard.\n";
	} 
	/*
	$sql =<<<EOF
      CREATE TABLE PLAYERS
      (LOGIN           TEXT    NOT NULL,
      MDP            TEXT     NOT NULL,
      EMAIL        TEXT);
EOF;

	$ret = $db->exec($sql);
	if(!$ret){
		echo $db->lastErrorMsg();
	} else {
		echo "Records created successfully\n";
	}	*/

	$pseudo = $_POST["pseudo"];
	$mdp = $_POST["mdp"];
	$mdpC = $_POST["mdpC"];
	$email = $_POST["email"];
	
	if(get_magic_quotes_gpc()===1) 
	{ 
     $pseudo = stripslashes($pseudo); 
     $mdp = stripslashes($mdp); 
	 $mdpC = stripslashes($mdpC); 
	 $email = stripslashes($email);
	} 

	/** 
	* On protège les chaînes 
	*/ 

    $pseudo = $db->escapeString($pseudo); 
    $mdp = $db->escapeString($mdp); 
	$mdpC = $db->escapeString($mdpC); 
    $email = $db->escapeString($email); 
	$mdp = hash('sha512', $mdp);
	$mdpC = hash('sha512', $mdpC);
	if ($mdpC==$mdp)
	{
		 
		$sql = $db->prepare("SELECT :pseudo FROM PLAYERS WHERE LOGIN=:pseudo ;");
		$sql->bindValue(':pseudo', $pseudo);
		$ret = $sql->execute();

		$n = 0;
		while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
		  $n += 1;
		}
		//echo $n;
		
		if($n!=0){
			echo "Ce pseudo est déjà utilisé.";
		} else {
			$sql = $db->prepare("INSERT INTO PLAYERS (LOGIN, MDP, EMAIL) VALUES (:pseudo, :mdp, :email);");
			$sql->bindValue(':pseudo', $pseudo);
			$sql->bindValue(':mdp', $mdp);
			$sql->bindValue(':email', $email);

			$ret = $sql->execute();
			if(!$ret){
				echo "Erreur ic";
			} else {
				echo "Compte crée avec succès \n";
			}
		}
	} else{
		echo "Les mots de passe ne sont pas identiques.\n";
	}	
	$db->close();
	
?>
>>>>>>> origin/Nicolas
