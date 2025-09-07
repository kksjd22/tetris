import pygame, random

pygame.init()
WIDTH, HEIGHT = 400, 600  # 多预留100px给右侧预览
CELL = 30
COLS, ROWS = 10, HEIGHT // CELL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris with Hard Drop & Preview")
clock = pygame.time.Clock()

# 方块形状
shapes = [
    [[1, 1, 1, 1]],                # I
    [[1, 1], [1, 1]],              # O
    [[0, 1, 0], [1, 1, 1]],        # T
    [[1, 0, 0], [1, 1, 1]],        # J
    [[0, 0, 1], [1, 1, 1]],        # L
    [[0, 1, 1], [1, 1, 0]],        # S
    [[1, 1, 0], [0, 1, 1]]         # Z
]

colors = [
    (0, 255, 255), (255, 255, 0),
    (128, 0, 128), (0, 0, 255),
    (255, 165, 0), (0, 255, 0),
    (255, 0, 0)
]

def new_piece():
    shape = random.choice(shapes)
    color = colors[shapes.index(shape)]
    return {"shape": shape, "x": COLS // 2 - len(shape[0]) // 2, "y": 0, "color": color}

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def valid(piece, grid):
    for y, row in enumerate(piece["shape"]):
        for x, val in enumerate(row):
            if val:
                nx, ny = piece["x"] + x, piece["y"] + y
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and grid[ny][nx] != (0,0,0):
                    return False
    return True

def lock_piece(piece, grid):
    for y, row in enumerate(piece["shape"]):
        for x, val in enumerate(row):
            if val:
                grid[piece["y"] + y][piece["x"] + x] = piece["color"]

def clear_lines(grid):
    lines_cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if (0,0,0) not in grid[y]:
            del grid[y]
            grid.insert(0, [(0,0,0)] * COLS)
            lines_cleared += 1
    return lines_cleared

def hard_drop(piece, grid):
    while True:
        moved = dict(piece)
        moved["y"] += 1
        if valid(moved, grid):
            piece = moved
        else:
            break
    return piece

# 初始化
grid = [[(0,0,0)] * COLS for _ in range(ROWS)]
piece = new_piece()
next_piece = new_piece()
fall_time = 0
speed = 0.5
score = 0
running = True

while running:
    screen.fill((0, 0, 0))
    fall_time += clock.get_time() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            moved = dict(piece)
            if event.key == pygame.K_LEFT:
                moved["x"] -= 1
                if valid(moved, grid):
                    piece = moved
            elif event.key == pygame.K_RIGHT:
                moved["x"] += 1
                if valid(moved, grid):
                    piece = moved
            elif event.key == pygame.K_DOWN:
                moved["y"] += 1
                if valid(moved, grid):
                    piece = moved
            elif event.key == pygame.K_UP:
                moved["shape"] = rotate(moved["shape"])
                if valid(moved, grid):
                    piece = moved
            elif event.key == pygame.K_SPACE:  # 硬降
                piece = hard_drop(piece, grid)
                lock_piece(piece, grid)
                score += clear_lines(grid) * 100
                piece = next_piece
                next_piece = new_piece()
                if not valid(piece, grid):
                    running = False

    # 自动下落
    if fall_time >= speed:
        moved = dict(piece)
        moved["y"] += 1
        if valid(moved, grid):
            piece = moved
        else:
            lock_piece(piece, grid)
            score += clear_lines(grid) * 100
            piece = next_piece
            next_piece = new_piece()
            if not valid(piece, grid):
                running = False
        fall_time = 0

    # 绘制固定方块
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != (0,0,0):
                pygame.draw.rect(screen, grid[y][x], (x*CELL, y*CELL, CELL-1, CELL-1))

    # 绘制当前方块
    for y, row in enumerate(piece["shape"]):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, piece["color"], ((piece["x"]+x)*CELL, (piece["y"]+y)*CELL, CELL-1, CELL-1))

    # 绘制右侧预览框
    pygame.draw.rect(screen, (50,50,50), (COLS*CELL, 0, 100, HEIGHT))
    font = pygame.font.SysFont("Arial", 20)
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (COLS*CELL + 10, 10))

    preview_text = font.render("Next:", True, (255,255,255))
    screen.blit(preview_text, (COLS*CELL + 10, 50))

     # 绘制下一个方块
    for y, row in enumerate(next_piece["shape"]):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, next_piece["color"], (COLS*CELL + 20 + x*CELL//1.5, 80 + y*CELL//1.5, CELL//1.5 - 1, CELL//1.5 - 1))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
print("Game Over! Final Score:", score)
