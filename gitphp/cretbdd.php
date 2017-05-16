<?php
/* USED TO CREATE THE DATABASES AT START


	class MyDB extends SQLite3
	{
		function __construct()
		{
			$this->open("login.db3");
		}
	}
	
	$db = new MyDB();
	if(!$db){
		echo "Erreur inconnue, veuillez réessayer plus tard.\n";
	} 
	
	$sql =<<<EOF
      CREATE TABLE LOGIN
      (TOKEN           TEXT    NOT NULL,
      TIME            INT     NOT NULL,
	  LOGIN            TEXT   NOT NULL);
EOF;

	$ret = $db->exec($sql);
	if(!$ret){
		echo $db->lastErrorMsg();
	} else {
		echo "Records created successfully\n";
	}	
$db->close()

*/
?>
