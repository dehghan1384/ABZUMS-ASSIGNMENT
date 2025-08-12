import numpy as np
import matplotlib.pyplot as plt

np.random.seed(2)
N = 256
keep_fraction = 0.65
sampling_mode = 'radial'
noise_level = 0.02
max_iter = 800
beta = 0.9
n_restarts = 3
positivity = True
use_HIO = True
verbose = True

def make_ground_truth(N):
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    g1 = np.exp(-((X+0.4)**2 + (Y+0.3)**2) / (2*(0.08)**2))
    g2 = 0.9 * np.exp(-((X-0.25)**2 + (Y-0.35)**2) / (2*(0.12)**2))
    r = np.sqrt(X**2 + Y**2)
    ring = (np.logical_and(r > 0.35, r < 0.48)).astype(float) * 0.6
    rect = ((np.abs(X) < 0.12) & (np.abs(Y+0.6) < 0.06)).astype(float) * 0.8
    img = 1.2 * g1 + g2 + ring + rect
    img = (img - img.min()) / (img.max() + 1e-12)
    return img

def make_support_mask_from_image(img):
    thresh = 0.07 * img.max()
    return (img > thresh).astype(float)

def make_fourier_sampling_mask(N, keep_fraction=0.65, mode='radial'):
    cx, cy = N // 2, N // 2
    xv, yv = np.arange(N) - cx, np.arange(N) - cy
    X, Y = np.meshgrid(xv, yv)
    r_norm = np.sqrt(X**2 + Y**2) / (np.sqrt((N//2)**2 + (N//2)**2) + 1e-12)
    if mode == 'random':
        total = N * N
        k = int(np.round(keep_fraction * total))
        idx = np.arange(total)
        pick = np.random.choice(idx, size=k, replace=False)
        mask = np.zeros(total, dtype=float)
        mask[pick] = 1.0
        mask = mask.reshape(N, N)
    else:
        alpha = 4.0
        probs = np.exp(-alpha * r_norm)
        probs /= probs.sum()
        total = N * N
        k = int(np.round(keep_fraction * total))
        flat = np.random.choice(np.arange(total), size=k, replace=False, p=probs.ravel())
        mask = np.zeros(total, dtype=float)
        mask[flat] = 1.0
        mask = mask.reshape(N, N)
    return mask

def add_noise_to_magnitude(Mtrue, mask, noise_level):
    noise = (1.0 + noise_level * np.random.randn(*Mtrue.shape))
    Mmeas = Mtrue * noise
    Mmeas *= mask
    return np.clip(Mmeas, 0.0, None)

def init_random_phase(Mmeas, measured_mask):
    measured_vals = Mmeas[measured_mask.astype(bool)]
    avg_mag = measured_vals.mean() if measured_vals.size else 1.0
    mag_init = Mmeas.copy()
    mag_init[measured_mask == 0] = avg_mag
    phase = np.random.uniform(-np.pi, np.pi, size=Mmeas.shape)
    return mag_init * np.exp(1j * phase)

def phase_retrieval(Mmeas, measured_mask, support_mask, params):
    max_iter = params['max_iter']
    beta = params['beta']
    positivity = params['positivity']
    use_HIO = params['use_HIO']
    n_restarts = params['n_restarts']
    verbose = params['verbose']
    best_rec, best_err, best_trace, best_spec = None, np.inf, None, None
    for restart in range(n_restarts):
        if verbose:
            print(f"Restart {restart+1}/{n_restarts}")
        S = init_random_phase(Mmeas, measured_mask)
        x = np.fft.ifft2(np.fft.ifftshift(S)).real
        err_trace = []
        for it in range(max_iter):
            S = np.fft.fftshift(np.fft.fft2(x))
            phase = np.angle(S)
            current_mag = np.abs(S)
            new_mag = current_mag.copy()
            new_mag[measured_mask.astype(bool)] = Mmeas[measured_mask.astype(bool)]
            S_new = new_mag * np.exp(1j * phase)
            x_new = np.fft.ifft2(np.fft.ifftshift(S_new)).real
            if use_HIO:
                inside = (support_mask > 0.5)
                outside = ~inside
                x_next = x.copy()
                x_next[inside] = x_new[inside]
                x_next[outside] = x[outside] - beta * x_new[outside]
                if positivity:
                    x_next[(x_next < 0) & inside] = 0.0
            else:
                x_next = x_new * support_mask
                if positivity:
                    x_next = np.clip(x_next, 0.0, None)
            mag_next = np.abs(np.fft.fftshift(np.fft.fft2(x_next)))
            denom = np.linalg.norm(Mmeas[measured_mask.astype(bool)]) + 1e-12
            err = np.linalg.norm((mag_next - Mmeas)[measured_mask.astype(bool)]) / denom
            err_trace.append(err)
            if verbose and (it % 200 == 0 or it == max_iter-1):
                print(f"  iter {it+1}/{max_iter}  rel-mag-err={err:.6f}")
            x = x_next
        if err_trace[-1] < best_err:
            best_err, best_rec, best_trace, best_spec = err_trace[-1], x.copy(), np.array(err_trace), S_new.copy()
    return best_rec, best_trace, best_spec

if __name__ == '__main__':
    gt = make_ground_truth(N)
    support = make_support_mask_from_image(gt)
    S_true = np.fft.fftshift(np.fft.fft2(gt))
    M_true = np.abs(S_true)
    sampling_mask = make_fourier_sampling_mask(N, keep_fraction, sampling_mode)
    Mmeas = add_noise_to_magnitude(M_true, sampling_mask, noise_level)
    params = dict(max_iter=max_iter, beta=beta, positivity=positivity, use_HIO=use_HIO, n_restarts=n_restarts, verbose=verbose)
    rec, trace, final_spec = phase_retrieval(Mmeas, sampling_mask, support, params)
    rec_scaled = (rec - rec.min()) / (rec.max() - rec.min() + 1e-12)
    residual = gt - rec_scaled
    nrmse = np.sqrt(np.mean((gt - rec_scaled)**2)) / (np.sqrt(np.mean(gt**2)) + 1e-12)
    corr = np.corrcoef(gt.ravel(), rec_scaled.ravel())[0, 1]
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    ax = axes.ravel()
    ax[0].imshow(gt, cmap='gray'); ax[0].set_title('Ground truth'); ax[0].axis('off')
    ax[1].imshow(support, cmap='gray'); ax[1].set_title('Support mask'); ax[1].axis('off')
    ax[2].imshow(np.log1p(Mmeas), cmap='inferno'); ax[2].set_title('Measured log-magnitude'); ax[2].axis('off')
    ax[3].imshow(sampling_mask, cmap='gray'); ax[3].set_title('Fourier sampling mask'); ax[3].axis('off')
    ax[4].imshow(rec_scaled, cmap='gray'); ax[4].set_title('Reconstruction'); ax[4].axis('off')
    ax[5].imshow(np.log1p(np.abs(final_spec)), cmap='inferno'); ax[5].set_title('Final log-magnitude'); ax[5].axis('off')
    ax[6].plot(trace); ax[6].set_title('Relative magnitude error'); ax[6].set_xlabel('Iteration'); ax[6].set_ylabel('Error'); ax[6].grid(True)
    ax[7].imshow(residual, cmap='bwr'); ax[7].set_title('Residual (GT - Recon)'); ax[7].axis('off')
    plt.tight_layout(); plt.show()
    print(f"Final rel-mag-error: {trace[-1]:.6f}")
    print(f"NRMSE: {nrmse:.6f}, Correlation: {corr:.6f}")
