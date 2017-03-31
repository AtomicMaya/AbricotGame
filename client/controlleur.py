# coding=utf-8
debug = True


def controler_types(*a_args, **a_kwargs):
    if debug:
        def decorateur(fonction_a_executer):
            def fonction_modifiee(*args, **kwargs):
                if (len(a_args) - len(a_kwargs) > len(args)) or (len(a_args) + len(a_kwargs) < len(args)):
                    raise SyntaxError("La fonction " + str(fonction_a_executer) + " attend " + str(
                        len(a_args)) + " arguments au lieu de " + str(len(args)))
                for i in range(len(a_args)):
                    if not (isinstance(args[i], a_args[i])):
                        raise SyntaxError("l'argument numero " + str(i + 1) + " n'est pas du type " + str(a_args[i]) +
                                          " mais du type " + str(type(args[i]))+" ( "+str(args[1])+" )")
                for cle in kwargs:
                    if cle not in a_kwargs:
                        raise SyntaxError("l'argument " + str(cle) + " n'existe pas")
                    if not (isinstance(kwargs[cle], a_kwargs[cle])):
                        raise SyntaxError("l'argument " + str(cle) + " n'est pas de type " + str(
                            a_kwargs[cle]) + " mais du type " + str(type(kwargs[cle])))
                return fonction_a_executer(*args, **kwargs)

            return fonction_modifiee

        return decorateur
    else:
        def decorateur(fonction_a_executer):
            def fonction_modifiee(*args, **kwargs):
                return fonction_a_executer(*args, **kwargs)

            return fonction_modifiee

        return decorateur
