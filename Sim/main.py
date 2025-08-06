from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeoMipTerrain, DirectionalLight, Vec3
from panda3d.core import CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue
from direct.task import Task

class TerrainApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Key mapping for movement
        self.keyMap = {"forward": False, "backward": False, "left": False, "right": False}

        # Accept key events
        self.accept("w", self.setKey, ["forward", True])
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])

        # 1. Create and configure terrain
        self.terrain = GeoMipTerrain("terrain")
        self.terrain.setHeightfield("assets/terrain/heightmap_fixed.png")
        self.terrain.setBlockSize(32)
        self.terrain.setNear(50)
        self.terrain.setFar(200)
        self.terrain.setFocalPoint(self.camera)
        self.terrain.setAutoFlatten(GeoMipTerrain.AFM_off)

        root = self.terrain.getRoot()
        root.reparentTo(self.render)
        root.setSz(60)  # vertical scale
        self.terrain.generate()
        from panda3d.core import Shader

        # Load textures
        self.grassTex = self.loader.loadTexture("assets/textures/ground_texture.jpg")
        self.rockTex = self.loader.loadTexture("assets/textures/rock_texture.jpg")
        self.snowTex = self.loader.loadTexture("assets/textures/snow_texture.jpg")

        # Load shader
        shader = Shader.load(Shader.SL_GLSL, "terrain_shader.vert", "terrain_shader.frag")
        root.setShader(shader)

        # Pass textures to shader
        root.setShaderInput("grassTex", self.grassTex)
        root.setShaderInput("rockTex", self.rockTex)
        root.setShaderInput("snowTex", self.snowTex)


        self.camera.setPos(128, 128, 20)
        self.camera.setScale(0.0000001)

        # 2. Setup terrain update + movement update
        self.taskMgr.add(self.updateTerrain, "updateTerrainTask")
        self.taskMgr.add(self.updateCamera, "updateCameraTask")

        # 3. Collision ray setup
        ray = CollisionRay()
        ray.setOrigin(0, 0, 10)  # ray starts slightly above camera
        ray.setDirection(0, 0, -1)

        rayNode = CollisionNode('camRay')
        rayNode.addSolid(ray)
        rayNode.setFromCollideMask(root.getCollideMask())
        rayNP = self.camera.attachNewNode(rayNode)

        self.camRayQueue = CollisionHandlerQueue()
        self.cTrav = CollisionTraverser()
        self.cTrav.addCollider(rayNP, self.camRayQueue)

    def setKey(self, key, value):
        self.keyMap[key] = value

    def updateTerrain(self, task):
        self.terrain.update()
        return task.cont

    def updateCamera(self, task):
        dt = globalClock.getDt()
        speed = 15
        direction = Vec3(0, 0, 0)

        if self.keyMap["forward"]: direction.y += speed * dt
        if self.keyMap["backward"]: direction.y -= speed * dt
        if self.keyMap["left"]: direction.x -= speed * dt
        if self.keyMap["right"]: direction.x += speed * dt

        self.camera.setPos(self.camera.getPos() + self.camera.getQuat().xform(direction))

        # Collision ray update
        self.cTrav.traverse(self.render)
        if self.camRayQueue.getNumEntries() > 0:
            self.camRayQueue.sortEntries()
            collision = self.camRayQueue.getEntry(0)
            terrainZ = collision.getSurfacePoint(self.render).getZ()
            self.camera.setZ(terrainZ + 2.0)  # lift camera slightly above terrain

        return task.cont

app = TerrainApp()
app.run()
