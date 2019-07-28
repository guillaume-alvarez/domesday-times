/**
 * Display a map loaded from json data using pixi.js lib.
 * It inserts itself in the <div> passed as a parameter.
 */
function PixiMap(div, width, height) {
    //Create the renderer
    var renderer = PIXI.autoDetectRenderer({ width: width, height: height, transparent: false });
    renderer.backgroundColor = 0x061639;

    var stage = new PIXI.Container();
    stage.interactive = true;
    stage.interactiveChildren = false;
    stage.hitArea = new PIXI.Rectangle(0, 0, width, height);
    var world = new PIXI.Container();
    world.sprites = new PIXI.ParticleContainer(200000);
    var camera = new Camera();
    var INIT_TILE_SIZE = 100.0
    var tileSize = INIT_TILE_SIZE;

    //Add the canvas to the HTML document
    div.appendChild(renderer.view);
    // IE9+, Chrome, Safari, Opera
    renderer.view.addEventListener("mousewheel", mouseWheelHandler, false);
    // Firefox
    renderer.view.addEventListener("DOMMouseScroll", mouseWheelHandler, false);

    PIXI.Loader.shared.reset();
    PIXI.Loader.shared
        .add("iconsTileset", iconsImagePath)
        .add("placesJson", "/api/places.json")
        .load(setup);

    function setup(loader, resources) {
        world.sprites.castle = new PIXI.Texture(resources.iconsTileset.texture.baseTexture, new PIXI.Rectangle(0, 0, 41, 41));
        world.sprites.village = new PIXI.Texture(resources.iconsTileset.texture.baseTexture, new PIXI.Rectangle(0, 41, 41, 41));
        world.sprites.textureSize = 41;
        tileSize *= world.sprites.textureSize;

        var roads = new PIXI.Graphics();
        roads.beginFill(0xFFFFFF, 0.0);
        roads.lineStyle(world.sprites.textureSize / 16, 0x9B870C, 1.0);

        var places = new Object();
        for (var i in resources.placesJson.data) {
            var place = resources.placesJson.data[i];
            places[place.id] = place;
        }

        for (var i in resources.placesJson.data) {
            var place = resources.placesJson.data[i];
            var sprite;
            if (place.type == 'Knights') {
                sprite = new PIXI.Sprite(world.sprites.castle);
            } else {
                sprite = new PIXI.Sprite(world.sprites.village);
            }
            sprite.position.x = place.longitude * tileSize - world.sprites.textureSize / 2;
            // latitude is from south, Y is from screen top
            sprite.position.y = -place.latitude * tileSize - world.sprites.textureSize / 2;

            // FIXME do not draw two times the same road
            for (var i in place.roads) {
                roads.moveTo(place.longitude * tileSize, -place.latitude * tileSize);
                var to = places[place.roads[i]];
                roads.lineTo(to.longitude * tileSize, -to.latitude * tileSize)
            }

            camera.include(sprite.position.x, sprite.position.y);
            world.sprites.addChild(sprite);
        }

        // required to be able to click on it
        var graphics = new PIXI.Graphics();
        graphics.beginFill(0xFFFFFF, 0);
        graphics.lineStyle(0);
        graphics.drawRect(0, 0, renderer.width, renderer.height);
        graphics.endFill();
        stage.addChildAt(graphics, 0);

        stage.addChild(world);

        var circle = new PIXI.Graphics();
        circle.beginFill(0xFFFFFF, 0.0);
        circle.lineStyle(world.sprites.textureSize / 8, 0x66FF66, 1.0);
        circle.drawCircle(0, 0, world.sprites.textureSize);
        circle.endFill();
        world.selectionCircle = renderer.generateTexture(circle);

        roads.endFill();
        world.addChild(roads);
        world.addChild(world.sprites);

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
            .on('pointermove', onDragMove)
            // events for user click on map
            .on('pointerdown', onSelect);

        camera.init(renderer, world, stage);
    }

    function mouseWheelHandler(e) {
        // reverse Firefox’s detail value
        var delta = e.wheelDelta || -e.detail;
        var pos = stage.toLocal(renderer.plugins.interaction.mouse.global)
        camera.zoomTo(0.1 * delta, pos.x, pos.y);
    }

    function onDragStart(event) {
        // store a reference to the data
        // the reason for this is because of multitouch
        // we want to track the movement of this particular touch
        world.dragStart = event.data.getLocalPosition(stage);
        // memorize original world position because using only delta often cause
        // approximations when there is any lag in the browser
        world.dragStart.x -= world.position.x;
        world.dragStart.y -= world.position.y;
        world.dragging = true;
    }

    function onDragEnd() {
        world.dragging = false;
        // set the interaction data to null
        world.dragStart = null;
    }

    function onDragMove(event) {
        if (world.dragging) {
            var newPosition = event.data.getLocalPosition(stage);
            camera.dragTo(newPosition.x - world.dragStart.x, newPosition.y - world.dragStart.y);
        }
    }

    function onSelect(event) {
        var pos = event.data.getLocalPosition(world);
        pos.x = pos.x / tileSize;
        pos.y = -pos.y / tileSize;
        console.log('onSelect ' + pos);
        var minDist = Math.pow(2 / INIT_TILE_SIZE, 2);
        var minPlace;
        function distance(pos, place) {
            return Math.pow(place.latitude - pos.y, 2) + Math.pow(place.longitude - pos.x, 2);
        }
        var places = PIXI.Loader.shared.resources.placesJson;
        for (var i in places.data) {
            var place = places.data[i];
            var dist = distance(pos, place);
            if (dist < minDist) {
                minDist = dist;
                minPlace = place;
            }
        }

        if (!minPlace) {
            console.log("Nothing selected, clicked at " + JSON.stringify(pos, null, 4));
            if (world.selectionSprite) {
                world.removeChild(world.selectionSprite);
                world.selectionSprite = null;
                renderer.render(stage);
            }
            return;
        }

        var place = minPlace;
        console.log("clicked on " + JSON.stringify(place, null, 4));

        if (world.selectionSprite) world.removeChild(world.selectionSprite);

        world.selectionSprite = new PIXI.Sprite(world.selectionCircle);
        world.selectionSprite.position.x = place.longitude * tileSize - world.sprites.textureSize;
        world.selectionSprite.position.y = -place.latitude * tileSize - world.sprites.textureSize;
        world.addChild(world.selectionSprite);
        renderer.render(stage);

        Actions.selectPlace(place.id);
    }

    // public function used from react components
    this.selectPlace = function (name) {
        var places = PIXI.Loader.shared.resources.placesJson;
        for (var i in places.data) {
            var place = places.data[i];
            if (name == place.name) {
                console.log("selected " + JSON.stringify(place, null, 4));

                if (world.selectionSprite) world.removeChild(world.selectionSprite);

                world.selectionSprite = new PIXI.Sprite(world.selectionCircle);
                world.selectionSprite.position.x = place.longitude * tileSize - world.sprites.textureSize;
                world.selectionSprite.position.y = -place.latitude * tileSize - world.sprites.textureSize;
                world.addChild(world.selectionSprite);

                camera.centerTo(place.longitude * tileSize, -place.latitude * tileSize)

                return place;
            }
        }

        console.log("Nothing selected from name '" + name + "'");
        if (world.selectionSprite) {
            world.removeChild(world.selectionSprite);
            world.selectionSprite = null;
            renderer.render(stage);
        }
        return null;
    }

}