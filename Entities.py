
class Entities:
    def __init__(self, asteroids = None, player = None):
        self.entitiesList = []
        self.bullets = []
        self.asteroids = asteroids
        self.player = player


    def addEntity(self, entity):
        self.entitiesList.append(entity)

    def addBullet(self, bullet):
        self.bullets.append(bullet)

    def getEntity(self, entity):
        for x in self.entitiesList:
            if x == entity:
                return x

    def update(self):
        self.asteroids.update()
        self.player.update()

        for bullet in self.bullets:
            bullet.update(self.asteroids)
            if bullet.dead:
                bullet.deleteNow()
                continue
            if bullet.y <= 0:
                bullet.deleteNow()



        self.bullets = [x for x in self.bullets if x.y > 0 and not x.dead]

        if(self.player.health <= 0):
            return True

        for entity in self.entitiesList:
            entity.update()

    def render(self):
        self.asteroids.render()
        self.player.render()

        for bullet in self.bullets:
            bullet.render()

        for entity in self.entitiesList:
            entity.render()
