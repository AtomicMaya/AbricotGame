<?php 
	class MyDB extends SQLite3
	{
		function __construct()
		{
			$this->open("players.db3");
		}
	}
	class MyDB2 extends SQLite3
	{
		function __construct()
		{
			$this->open("login.db3");
		}
	}
	
	$db = new MyDB();
	if(!$db){
		echo "0x Erreur inconnue, veuillez réessayer plus tard.\n";
	} 

	$pseudo = $_POST["pseudo"];
	$mdp = $_POST["mdp"];
	
	if(get_magic_quotes_gpc()===1) 
	{ 
     $pseudo = stripslashes($pseudo); 
     $mdp = stripslashes($mdp); 
	 $email = stripslashes($email);
	} 

	/** 
	* On protège les chaînes 
	*/ 

    $pseudo = $db->escapeString($pseudo); 
    $mdp = $db->escapeString($mdp); 
	 
	$sql = $db->prepare("SELECT :pseudo FROM PLAYERS WHERE LOGIN=:pseudo AND MDP=:mdp;");
	$sql->bindValue(':pseudo', $pseudo);
	$sql->bindValue(':mdp', $mdp);
	$ret = $sql->execute();

	$n = 0;
	while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
      $n += 1;
	}
	//echo $n;
	
	if($n==0){
		echo "Nom de compte ou mot de passe erroné.\n";
	} else {
		$token = bin2hex(random_bytes(32));
		$db2 = new MyDB2();
		if(!$db2){
			echo "0x Erreur inconnue, veuillez réessayer plus tard.\n";
		} else
		{
			$sql = $db2->prepare("INSERT INTO LOGIN (TOKEN, TIME, LOGIN) VALUES (:token, :time, :pseudo);");
			$sql->bindValue(':pseudo', $pseudo);
			$sql->bindValue(':token', $token);
			$sql->bindValue(':time', time());
			
			$ret = $sql->execute();
			if(!$ret){
				echo "0x Erreur icn";
			} else {
				echo $token;
			}
		}
		$db2->close();
	}
	
$db->close();
	
?>
