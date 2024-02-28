import random
import noise
import numpy as np
from PIL import Image

# Generate the height map using Simplex Noise
def generate_perlin_height_map(width, height, scale, octaves, persistence, lacunarity, seed):
    # Create an array of size width and height filled with 0s
    world = np.zeros((width, height))

    # Iterate through every element of the array
    for i in range(width):
        for j in range(height):
            # set the value of the current element of the height map
            world[i][j] = (
                    noise.snoise2(i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                  repeatx=1024, repeaty=1024, base=seed) +
                    noise.snoise2(i / scale, j / scale, octaves=1, persistence=persistence, lacunarity=lacunarity,
                                  repeatx=1024, repeaty=1024, base=seed // 2) -
                    2 * noise.snoise2(i / scale, j / scale, octaves=4, persistence=persistence, lacunarity=lacunarity,
                                  repeatx=1024, repeaty=1024, base=seed // 3)
            )

    # ChatGPT gave me this shit. Don't question it.
    world = (world - np.min(world)) / (np.max(world) - np.min(world))
    y, x = np.ogrid[:width, :height]
    center_x, center_y = width / 2, height / 2
    mask = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) / (width * 1.5 / 2)
    world *= np.clip(1.0 - mask, 0, 1)
    # Return the height map array
    return world

# Save Image
def save_image(image_array, filename):
    image = Image.fromarray((image_array * 255).astype(np.uint8))
    image.save(filename)

# Process Map - Create the final output
def process_map(height_map, cloud):
    # Create an image with width / height of the final output
    terrain = Image.new("RGB", (height_map.shape[0], height_map.shape[1]))
    for x in range(height_map.shape[0]):
        for y in range(height_map.shape[1]):
            # Set the pixel colour based on height
            pixel_color = (0, 0, 200) if height_map[x][y] < 0.3 else (190, 190, 200) if height_map[x][y] > 0.55 else (
            242, 203, 143) if height_map[x][y] < 0.33 else (0, 155, 0)
            terrain.putpixel((x, y), pixel_color)

            # get the current pixel
            pixel = terrain.getpixel((x, y))
            # calculate the height difference
            height_difference = height_map[x - 8][y - 4] - height_map[x][y]
            # scaling factor
            scaling_factor = 1500 * height_map[x][y]
            # Change the color based on height difference
            color = (
                int(pixel[0] - height_difference * scaling_factor),
                int(pixel[1] - height_difference * scaling_factor),
                int(pixel[2] - height_difference * scaling_factor)
            )
            # Set the pixel to the determined color
            terrain.putpixel((x, y), color)

    for x in range(cloud.shape[0]):
        for y in range(cloud.shape[1]):
            if cloud[x][y] > 0.7:
                terrain.putpixel((x, y), (225, 225, 225))
            if cloud[x - 8][y - 2] > 0.7 > cloud[x][y] and x - 8 > -1 and y - 4 > -1:
                pixel = terrain.getpixel((x, y))
                color = (
                    int(pixel[0] * 0.5),
                    int(pixel[1] * 0.5),
                    int(pixel[2] * 0.5)
                )
                terrain.putpixel((x, y), color)
            pixel = terrain.getpixel((x, y))
            if pixel == (225, 225, 225):
                height_difference = cloud[x - 6][y - 3] - cloud[x][y]
                scaling_factor = 1800 * cloud[x][y]
                color = (
                    int(pixel[0] - height_difference * scaling_factor),
                    int(pixel[1] - height_difference * scaling_factor),
                    int(pixel[2] - height_difference * scaling_factor)
                )
                terrain.putpixel((x, y), color)

    return terrain

def clouds(width, height, scale, persistence, lacunarity, seed):
    world = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            world[i][j] = (
                    noise.pnoise2(i / scale, j / scale, octaves=2, persistence=persistence, lacunarity=lacunarity,
                                  repeatx=1024, repeaty=1024, base=seed)
                    + noise.pnoise2(i / scale, j / scale, octaves=3, persistence=persistence, lacunarity=lacunarity,
                                    repeatx=1024, repeaty=1024, base=seed + 3)
            )

    world = (world - np.min(world)) / (np.max(world) - np.min(world))

    return world


if __name__ == "__main__":
    width, height = 1000, 1000
    scale, octaves, persistence, lacunarity = 250, 8, 0.5, 2.4
    for i in range(0, 1):
        seed = random.randint(0, 100)
        height_map = generate_perlin_height_map(width, height, scale, octaves, persistence, lacunarity, seed)

        cloud = clouds(width, height, scale, persistence, lacunarity, seed)
        save_image(cloud, f"processed/clouds/cloud_x{scale}_{i}.png")
        processed_map = process_map(height_map, cloud)

        processed_map.save(f"processed/backgrounds/processed_island_x{width}_{seed}.png")
        print(f"Processed ", i)
