
//Create the renderer
var renderer = PIXI.autoDetectRenderer(256, 256);
renderer.view.style.border = "1px dashed black";
renderer.backgroundColor = 0x061639;
renderer.view.style.position = "absolute";
renderer.view.style.display = "block";
renderer.autoResize = true;
renderer.resize(window.innerWidth - 10, window.innerHeight - 10);

//Add the canvas to the HTML document
document.body.appendChild(renderer.view);

//Create a container object called the `stage`

//Tell the `renderer` to `render` the `stage`
var stage = new PIXI.Container();
renderer.render(stage);

var Camera = function() {
    this.x = Number.MAX_SAFE_INTEGER;
    this.y = Number.MAX_SAFE_INTEGER;
    this.width = 0;
    this.height = 0;
};
Camera.prototype.include = function(x, y) {
    if (x < this.x) this.x = x;
    else if (x - this.x > this.width) this.width = x - this.x;
    if (y < this.y) this.y = y;
    else if (y - this.y > this.height) this.height = y - this.y;
};
Camera.prototype.scale = function(renderer) {
    scaleX = renderer.width / this.width;
    scaleY = renderer.height / this.height;
    return Math.min(scaleX, scaleY);
};

PIXI.loader
    .add("villageImage", villageImage)
    .add("placesJson", placesJson)

    .load(function (loader, resources) {
        var container = new PIXI.ParticleContainer();
        var texture = resources.villageImage.texture;
        var camera = new Camera();

        for (var i in resources.placesJson.data) {
            var sprite = new PIXI.Sprite(texture);
            var place = resources.placesJson.data[i];
            sprite.position.x = place.fields.longitude * texture.width * 100.0;
            // latitude is from south, Y is from screen top
            sprite.position.y = -place.fields.latitude * texture.height * 100.0;

            camera.include(sprite.position.x, sprite.position.y);
            container.addChild(sprite);
        }


        var scale = camera.scale(renderer);
        container.scale.x = scale;
        container.scale.y = scale;

        container.position.x = -(camera.x - 10) * scale;
        container.position.y = -(camera.y - 10) * scale;

        stage.addChild(container);
        renderer.render(stage);
    });