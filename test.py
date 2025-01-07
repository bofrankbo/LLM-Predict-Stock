# 定義父類別
class Animal:
    def __init__(self, name):
        self.name = name
        self.a = 0

    def speak(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def eat(self):
        return f"{self.name} is eating!"

    def printb(self, b):
        print(b)
    
    def printa(self):
        print(self.a)


# 定義子類別，繼承自 Animal
class Dog(Animal):
    def __init__(self, name):
        self.name = name
        self.a = 10
        
    def speak(self):
        return f"{self.name} says Woof! {self.a}"
    
    def printa(self):
        print(self.a)

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

# 使用子類別
dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.a)  # 輸出: Buddy says Woof!
print(cat.speak())  # 輸出: Whiskers says Meow!