
//Create the renderer
var renderer = PIXI.autoDetectRenderer(256, 256);
renderer.backgroundColor = 0x061639;
renderer.view.style.position = "absolute";
renderer.view.style.display = "block";
renderer.autoResize = true;
// 10px for scroll bars and such
renderer.resize(window.innerWidth - 10, window.innerHeight - 10);

var stage = new PIXI.Container();
stage.interactive = true;
var world = new PIXI.ParticleContainer();
var camera = new Camera();

//Add the canvas to the HTML document
document.body.appendChild(renderer.view);
// IE9+, Chrome, Safari, Opera
document.addEventListener("mousewheel", mouseWheelHandler, false);
// Firefox
document.addEventListener("DOMMouseScroll", mouseWheelHandler, false);


PIXI.loader
    .add("villageImage", villageImage)
    .add("placesJson", placesJson)
    .load(setup);

function setup(loader, resources) {
    var texture = resources.villageImage.texture;

    for (var i in resources.placesJson.data) {
        var sprite = new PIXI.Sprite(texture);
        var place = resources.placesJson.data[i];
        sprite.position.x = place.fields.longitude * texture.width * 100.0;
        // latitude is from south, Y is from screen top
        sprite.position.y = -place.fields.latitude * texture.height * 100.0;

        camera.include(sprite.position.x, sprite.position.y);
        world.addChild(sprite);
    }

    // required to be able to click on it
    var graphics = new PIXI.Graphics();
    graphics.beginFill(0xFFFFFF, 0);
    graphics.lineStyle(0);
    graphics.drawRect(0, 0, renderer.width, renderer.height);
    graphics.endFill();
    stage.addChildAt(graphics, 0);

    stage.addChild(world);

    // setup events
    stage
        // events for drag start
        .on('mousedown', onDragStart)
        .on('touchstart', onDragStart)
        // events for drag end
        .on('mouseup', onDragEnd)
        .on('mouseupoutside', onDragEnd)
        .on('touchend', onDragEnd)
        .on('touchendoutside', onDragEnd)
        // events for drag move
        .on('mousemove', onDragMove)
        .on('touchmove', onDragMove);


    camera.init(renderer, world, stage);
}

function mouseWheelHandler(e) {
    // reverse Firefox’s detail value
    var delta = e.wheelDelta || -e.detail;
    camera.zoom(0.1 * delta);
}

function onDragStart(event) {
    // store a reference to the data
    // the reason for this is because of multitouch
    // we want to track the movement of this particular touch
    world.dragStart = event.data.getLocalPosition(world.parent);
    world.dragStart.x -= world.position.x;
    world.dragStart.y -= world.position.y;
    world.dragging = true;
}

function onDragEnd() {
    world.dragging = false;
    // set the interaction data to null
    world.data = null;
}

function onDragMove(event) {
    if (world.dragging) {
        var newPosition = event.data.getLocalPosition(world.parent);
        world.position.x = newPosition.x - world.dragStart.x;
        world.position.y = newPosition.y - world.dragStart.y;
        renderer.render(stage);
    }
}