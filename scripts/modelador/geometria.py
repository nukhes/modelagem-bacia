import numpy as np
from scipy.interpolate import RBFInterpolator

def obter_grid_interpolado(pontos_x, pontos_y, valores_z, dx, dy, min_x, min_y, resolucao_grid, angulo_graus, razao_anisotropia, suavizacao):
    """
    Interpolação RBF com anisotropia e suavização.
    """
    z_vals = np.asarray(valores_z, dtype=float)

    if np.isnan(z_vals).all() or z_vals.size == 0:
        raise ValueError('valores de z são inválidos')

    if dx <= 0 or dy <= 0:
        raise ValueError('dx e dy devem ser positivos para gerar o grid.')
    
    pts = np.column_stack((pontos_x, pontos_y)).astype(float)
    
    if pts.shape[0] != z_vals.shape[0]:
        raise ValueError('O número de pontos não corresponde ao número de valores z.')

    
    # se temos menos de 3 valores não podemos montar um plano, então retornamos
    # um grid constante com a média dos valores disponíveis, futuramente
    # podemos explorar outras estratégias com vizinhos ou algo do tipo.
    unique_pts = np.unique(pts, axis=0)
    if unique_pts.shape[0] < 3:
        return np.full((resolucao_grid, resolucao_grid), np.nanmean(z_vals), dtype=float)

    # este é o caso ideal, temos pontos suficientes para interpolar
    centro_x = min_x + dx / 2.0
    centro_y = min_y + dy / 2.0
    pts[:, 0] -= centro_x
    pts[:, 1] -= centro_y

    theta = np.radians(angulo_graus)
    rotacao = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    
    # a anisotropia é aplicada pois quando usamos interpolação a 'influência'
    # de um ponto na superfície é um círculo perfeito, com anisotropia podemos
    # distorcer em uma direção gerando uma elipse, isso é útil para modelar
    # formações geológicas que tem um comportamento mais linear em uma direção.
    escalonamento = np.array([
        [1.0, 0.0],
        [0.0, 1.0 / razao_anisotropia]
    ])
    transformacao = rotacao @ escalonamento
    pts_transformados = pts @ transformacao

    rbf = RBFInterpolator(
        pts_transformados,
        z_vals,
        kernel='thin_plate_spline',
        smoothing=suavizacao,
    )

    grid_x = np.linspace(-dx / 2.0, dx / 2.0, resolucao_grid)
    grid_y = np.linspace(-dy / 2.0, dy / 2.0, resolucao_grid)
    X, Y = np.meshgrid(grid_x, grid_y)

    grid_pts = np.column_stack((X.ravel(), Y.ravel()))
    grid_pts_transf = grid_pts @ transformacao

    z_grid = rbf(grid_pts_transf).reshape(resolucao_grid, resolucao_grid)
    return z_grid