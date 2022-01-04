# (c) @AbirHasan2005

import random

__chars = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z " \
          "a b c d e f g h i j k l m n o p q r s t u v w x y z " \
          "1 2 3 4 5 6 7 8 9 0".split()


def generate_rnd_id():
    __id = "fa"
    for i in range(15):
        __id += f"{random.choice(__chars)}"
    return __id
