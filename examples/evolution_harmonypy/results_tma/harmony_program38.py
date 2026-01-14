# harmonypy - A data alignment algorithm.
# Copyright (C) 2018  Ilya Korsunsky
#               2019  Kamil Slowikowski <kslowikowski@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
import numpy as np
import torch
from sklearn.cluster import KMeans
import logging

# create logger
logger = logging.getLogger('harmonypy')
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def get_device(device=None):
    """Get the appropriate device for PyTorch operations."""
    if device is not None:
        return torch.device(device)

    # Check for available accelerators
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device('mps')
    else:
        return torch.device('cpu')


def run_harmony(
    data_mat: np.ndarray,
    meta_data: pd.DataFrame,
    vars_use,
    theta=None,
    lamb=None,
    sigma=0.1,
    nclust=None,
    tau=0,
    block_size=0.05,
    max_iter_harmony=10,
    max_iter_kmeans=20,
    epsilon_cluster=1e-5,
    epsilon_harmony=1e-4,
    alpha=0.2,
    verbose=True,
    random_state=0,
    device=None
):
    """Run Harmony batch effect correction.

    This is a PyTorch implementation matching the R package formulas.
    Supports CPU and GPU (CUDA, MPS) acceleration.

    Parameters
    ----------
    data_mat : np.ndarray
        PCA embedding matrix (cells x PCs or PCs x cells)
    meta_data : pd.DataFrame
        Metadata with batch variables (cells x variables)
    vars_use : str or list
        Column name(s) in meta_data to use for batch correction
    theta : float or list, optional
        Diversity penalty parameter(s). Default is 2 for each batch.
    lamb : float or list, optional
        Ridge regression penalty. Default is 1 for each batch.
        If -1, lambda is estimated automatically (matches R package).
    sigma : float, optional
        Kernel bandwidth for soft clustering. Default is 0.1.
    nclust : int, optional
        Number of clusters. Default is min(N/30, 100).
    tau : float, optional
        Protection against overcorrection. Default is 0.
    block_size : float, optional
        Proportion of cells to update in each block. Default is 0.05.
    max_iter_harmony : int, optional
        Maximum Harmony iterations. Default is 10.
    max_iter_kmeans : int, optional
        Maximum k-means iterations per Harmony iteration. Default is 20.
    epsilon_cluster : float, optional
        K-means convergence threshold. Default is 1e-5.
    epsilon_harmony : float, optional
        Harmony convergence threshold. Default is 1e-4.
    alpha : float, optional
        Alpha parameter for lambda estimation (when lamb=-1). Default is 0.2.
    verbose : bool, optional
        Print progress messages. Default is True.
    random_state : int, optional
        Random seed for reproducibility. Default is 0.
    device : str, optional
        Device to use ('cpu', 'cuda', 'mps'). Default is auto-detect.

    Returns
    -------
    Harmony
        Harmony object with corrected data in Z_corr attribute.
    """
    N = meta_data.shape[0]
    if data_mat.shape[1] != N:
        data_mat = data_mat.T

    assert data_mat.shape[1] == N, \
       "data_mat and meta_data do not have the same number of cells"

    if nclust is None:
        nclust = int(min(round(N / 30.0), 100))

    if isinstance(sigma, float) and nclust > 1:
        sigma = np.repeat(sigma, nclust)

    if isinstance(vars_use, str):
        vars_use = [vars_use]

    # Create batch indicator matrix (one-hot encoded)
    phi = pd.get_dummies(meta_data[vars_use]).to_numpy().T.astype(np.float32)
    phi_n = meta_data[vars_use].describe().loc['unique'].to_numpy().astype(int)

    # Theta handling - default is 2 (matches R package)
    if theta is None:
        theta = np.repeat([2] * len(phi_n), phi_n).astype(np.float32)
    elif isinstance(theta, (float, int)):
        theta = np.repeat([theta] * len(phi_n), phi_n).astype(np.float32)
    elif len(theta) == len(phi_n):
        theta = np.repeat([theta], phi_n).astype(np.float32)
    else:
        theta = np.asarray(theta, dtype=np.float32)

    assert len(theta) == np.sum(phi_n), \
        "each batch variable must have a theta"

    # Lambda handling (matches R package)
    lambda_estimation = False
    if lamb is None:
        lamb = np.repeat([1] * len(phi_n), phi_n).astype(np.float32)
        lamb = np.insert(lamb, 0, 0).astype(np.float32)
    elif lamb == -1:
        lambda_estimation = True
        lamb = np.zeros(1, dtype=np.float32)
    elif isinstance(lamb, (float, int)):
        lamb = np.repeat([lamb] * len(phi_n), phi_n).astype(np.float32)
        lamb = np.insert(lamb, 0, 0).astype(np.float32)
    elif len(lamb) == len(phi_n):
        lamb = np.repeat([lamb], phi_n).astype(np.float32)
        lamb = np.insert(lamb, 0, 0).astype(np.float32)
    else:
        lamb = np.asarray(lamb, dtype=np.float32)
        if len(lamb) == np.sum(phi_n):
            lamb = np.insert(lamb, 0, 0).astype(np.float32)

    # Number of items in each category
    N_b = phi.sum(axis=1)
    Pr_b = (N_b / N).astype(np.float32)

    if tau > 0:
        theta = theta * (1 - np.exp(-(N_b / (nclust * tau)) ** 2))

    # Get device
    device_obj = get_device(device)

    if verbose:
        logger.info(f"Running Harmony (PyTorch on {device_obj})")
        logger.info("  Parameters:")
        logger.info(f"    max_iter_harmony: {max_iter_harmony}")
        logger.info(f"    max_iter_kmeans: {max_iter_kmeans}")
        logger.info(f"    epsilon_cluster: {epsilon_cluster}")
        logger.info(f"    epsilon_harmony: {epsilon_harmony}")
        logger.info(f"    nclust: {nclust}")
        logger.info(f"    block_size: {block_size}")
        if lambda_estimation:
            logger.info(f"    lamb: dynamic (alpha={alpha})")
        else:
            logger.info(f"    lamb: {lamb[1:]}")
        logger.info(f"    theta: {theta}")
        logger.info(f"    sigma: {sigma[:5]}..." if len(sigma) > 5 else f"    sigma: {sigma}")
        logger.info(f"    verbose: {verbose}")
        logger.info(f"    random_state: {random_state}")
        logger.info(f"  Data: {data_mat.shape[0]} PCs 脳 {N} cells")
        logger.info(f"  Batch variables: {vars_use}")

    # Set random seeds
    np.random.seed(random_state)
    torch.manual_seed(random_state)

    # Optional: enable TF32 on CUDA for faster matmuls (distance updates)
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True

    # Ensure data_mat is a proper numpy array
    if hasattr(data_mat, 'values'):
        data_mat = data_mat.values
    data_mat = np.asarray(data_mat, dtype=np.float32)

    ho = Harmony(
        data_mat, phi, Pr_b, sigma.astype(np.float32),
        theta, lamb, alpha, lambda_estimation,
        max_iter_harmony, max_iter_kmeans,
        epsilon_cluster, epsilon_harmony, nclust, block_size, verbose,
        random_state, device_obj
    )

    # Use tau as a trust-region / proximal step strength during correction:
    # tau <= 0 disables explicit displacement limiting.
    ho._tau_trust = float(tau)

    return ho


class Harmony:
    """Harmony class for batch effect correction using PyTorch.

    Supports CPU and GPU acceleration.
    """

    def __init__(
            self, Z, Phi, Pr_b, sigma, theta, lamb, alpha, lambda_estimation,
            max_iter_harmony, max_iter_kmeans,
            epsilon_kmeans, epsilon_harmony, K, block_size, verbose,
            random_state, device
    ):
        self.device = device

        # Convert to PyTorch tensors on device
        # Store with underscore prefix internally, expose as properties returning NumPy arrays
        self._Z_corr = torch.tensor(Z, dtype=torch.float32, device=device)
        self._Z_orig = torch.tensor(Z, dtype=torch.float32, device=device)

        # Simple L2 normalization (faster/stabler than torch.linalg.norm in hot paths)
        den = torch.rsqrt((self._Z_orig * self._Z_orig).sum(dim=0, keepdim=True).clamp_min(1e-12))
        self._Z_cos = self._Z_orig * den

        # Batch indicators
        self._Phi = torch.tensor(Phi, dtype=torch.float32, device=device)
        self._Pr_b = torch.tensor(Pr_b, dtype=torch.float32, device=device)

        # Precompute batch id per cell (assumes one-hot Phi)
        self._batch_id = self._Phi.argmax(dim=0).to(torch.long)

        self.N = self._Z_corr.shape[1]
        self.B = Phi.shape[0]
        self.d = self._Z_corr.shape[0]

        # Build batch index for fast ridge correction
        self._batch_index = []
        for b in range(self.B):
            idx = torch.where(self._Phi[b, :] > 0)[0]
            self._batch_index.append(idx)

        # Create Phi_moe with intercept
        ones = torch.ones(1, self.N, dtype=torch.float32, device=device)
        self._Phi_moe = torch.cat([ones, self._Phi], dim=0)

        self.window_size = 3
        self.epsilon_kmeans = epsilon_kmeans
        self.epsilon_harmony = epsilon_harmony

        self._lamb = torch.tensor(lamb, dtype=torch.float32, device=device)
        self.alpha = alpha
        self.lambda_estimation = lambda_estimation
        self._sigma = torch.tensor(sigma, dtype=torch.float32, device=device)
        self.block_size = block_size
        self.K = K
        self.max_iter_harmony = max_iter_harmony
        self.max_iter_kmeans = max_iter_kmeans
        self.verbose = verbose
        self._theta = torch.tensor(theta, dtype=torch.float32, device=device)

        # Dirichlet prior strength for KL-to-target batch composition penalty.
        # Deterministic (no public API change). Larger => smoother/stabler penalty.
        # Typical scale: ~O(N/K)
        self._beta = float(0.01 * self.N / max(self.K, 1))

        # Trust-region / proximal correction strength (set from run_harmony tau).
        # tau <= 0 disables displacement limiting.
        self._tau_trust = 0.0

        self.objective_harmony = []
        self.objective_kmeans = []
        self.objective_kmeans_dist = []
        self.objective_kmeans_entropy = []
        self.objective_kmeans_cross = []
        self.kmeans_rounds = []

        self.allocate_buffers()
        self.init_cluster(random_state)
        self.harmonize(self.max_iter_harmony, self.verbose)

    # =========================================================================
    # Properties - Return NumPy arrays for inspection and tutorials
    # =========================================================================

    @property
    def Z_corr(self):
        """Corrected embedding matrix (N x d). Batch effects removed."""
        return self._Z_corr.cpu().numpy().T

    @property
    def Z_orig(self):
        """Original embedding matrix (N x d). Input data before correction."""
        return self._Z_orig.cpu().numpy().T

    @property
    def Z_cos(self):
        """L2-normalized embedding matrix (N x d). Used for clustering."""
        return self._Z_cos.cpu().numpy().T

    @property
    def R(self):
        """Soft cluster assignment matrix (N x K). R[i,k] = P(cell i in cluster k)."""
        return self._R.cpu().numpy().T

    @property
    def Y(self):
        """Cluster centroids matrix (d x K). Columns are cluster centers."""
        return self._Y.cpu().numpy()

    @property
    def O(self):
        """Observed batch-cluster counts (K x B). O[k,b] = sum of R[k,:] for batch b."""
        return self._O.cpu().numpy()

    @property
    def E(self):
        """Expected batch-cluster counts (K x B). E[k,b] = cluster_size[k] * batch_proportion[b]."""
        return self._E.cpu().numpy()

    @property
    def Phi(self):
        """Batch indicator matrix (N x B). One-hot encoding of batch membership."""
        return self._Phi.cpu().numpy().T

    @property
    def Phi_moe(self):
        """Batch indicator with intercept (N x (B+1)). First column is all ones."""
        return self._Phi_moe.cpu().numpy().T

    @property
    def Pr_b(self):
        """Batch proportions (B,). Pr_b[b] = cells in batch b / total cells."""
        return self._Pr_b.cpu().numpy()

    @property
    def theta(self):
        """Diversity penalty parameters (B,). Higher = more mixing encouraged."""
        return self._theta.cpu().numpy()

    @property
    def sigma(self):
        """Clustering bandwidth parameters (K,). Soft assignment kernel width."""
        return self._sigma.cpu().numpy()

    @property
    def lamb(self):
        """Ridge regression penalty ((B+1),). Regularization for batch correction."""
        return self._lamb.cpu().numpy()

    @property
    def objectives(self):
        """List of objective values for compatibility with evaluator."""
        return self.objective_harmony

    def result(self):
        """Return corrected data as NumPy array."""
        return self._Z_corr.cpu().numpy().T

    def allocate_buffers(self):
        self._scale_dist = torch.zeros((self.K, self.N), dtype=torch.float32, device=self.device)
        self._dist_mat = torch.zeros((self.K, self.N), dtype=torch.float32, device=self.device)
        self._O = torch.zeros((self.K, self.B), dtype=torch.float32, device=self.device)
        self._E = torch.zeros((self.K, self.B), dtype=torch.float32, device=self.device)
        self._W = torch.zeros((self.B + 1, self.d), dtype=torch.float32, device=self.device)
        self._R = torch.zeros((self.K, self.N), dtype=torch.float32, device=self.device)
        self._Y = torch.zeros((self.d, self.K), dtype=torch.float32, device=self.device)

    def init_cluster(self, random_state):
        logger.info("Computing initial centroids with sklearn.KMeans...")
        # KMeans needs CPU numpy array
        Z_cos_np = self._Z_cos.cpu().numpy()
        model = KMeans(n_clusters=self.K, init='k-means++',
                       n_init=1, max_iter=25, random_state=random_state)
        model.fit(Z_cos_np.T)
        self._Y = torch.tensor(model.cluster_centers_.T, dtype=torch.float32, device=self.device)
        logger.info("KMeans initialization complete.")

        # Normalize centroids (faster/stabler)
        den = torch.rsqrt((self._Y * self._Y).sum(dim=0, keepdim=True).clamp_min(1e-12))
        self._Y = self._Y * den

        # Make contiguous for faster GEMMs
        self._Y = self._Y.contiguous()
        self._Z_cos = self._Z_cos.contiguous()

        # Compute distance matrix: dist = 2 * (1 - Y.T @ Z_cos)
        self._dist_mat = 2 * (1 - self._Y.T @ self._Z_cos)

        # Compute R
        self._R = -self._dist_mat / self._sigma[:, None]
        self._R = torch.exp(self._R)
        self._R = self._R / self._R.sum(dim=0)

        # Batch diversity statistics
        self._E = torch.outer(self._R.sum(dim=1), self._Pr_b)
        self._O = self._R @ self._Phi.T

        self.compute_objective()
        self.objective_harmony.append(self.objective_kmeans[-1])

    def compute_objective(self):
        # Normalization constant
        norm_const = 2000.0 / self.N

        # K-means error
        kmeans_error = torch.sum(self._R * self._dist_mat).item()

        # Entropy
        _entropy = torch.sum(safe_entropy_torch(self._R) * self._sigma[:, None]).item()

        # Cross entropy (R package formula) with numerical stability
        R_sigma = self._R * self._sigma[:, None]
        # Clamp to avoid log(0) or division by zero
        O_clamped = torch.clamp(self._O, min=1e-8)
        E_clamped = torch.clamp(self._E, min=1e-8)
        ratio = (O_clamped + E_clamped) / E_clamped
        theta_log = self._theta.unsqueeze(0).expand(self.K, -1) * torch.log(ratio)

        # Avoid (KxB)@(BxN) by gathering one-hot batch columns
        theta_log_per_cell = theta_log.index_select(1, self._batch_id)  # (K, N)
        _cross_entropy = torch.sum(R_sigma * theta_log_per_cell).item()

        # Store with normalization constant
        self.objective_kmeans.append((kmeans_error + _entropy + _cross_entropy) * norm_const)
        self.objective_kmeans_dist.append(kmeans_error * norm_const)
        self.objective_kmeans_entropy.append(_entropy * norm_const)
        self.objective_kmeans_cross.append(_cross_entropy * norm_const)

    def harmonize(self, iter_harmony=10, verbose=True):
        converged = False
        for i in range(1, iter_harmony + 1):
            if verbose:
                logger.info(f"Iteration {i} of {iter_harmony}")

            self.cluster()
            self.moe_correct_ridge()

            converged = self.check_convergence(1)
            if converged:
                if verbose:
                    logger.info(f"Converged after {i} iteration{'s' if i > 1 else ''}")
                break

        if verbose and not converged:
            logger.info("Stopped before convergence")

    def cluster(self):
        self._dist_mat = 2 * (1 - self._Y.T @ self._Z_cos)

        rounds = 0
        for i in range(self.max_iter_kmeans):
            # Update Y
            self._Y = self._Z_cos @ self._R.T
            den = torch.rsqrt((self._Y * self._Y).sum(dim=0, keepdim=True).clamp_min(1e-12))
            self._Y = self._Y * den

            # Update distance matrix
            self._dist_mat = 2 * (1 - self._Y.T @ self._Z_cos)

            # Update R
            self.update_R()

            # Compute objective and check convergence
            self.compute_objective()

            if i > self.window_size:
                if self.check_convergence(0):
                    rounds = i + 1
                    break
            rounds = i + 1

        self.kmeans_rounds.append(rounds)
        self.objective_harmony.append(self.objective_kmeans[-1])

    def update_R(self):
        # Create shuffled update order
        update_order = torch.randperm(self.N, device=self.device)

        # Process in blocks
        n_blocks = int(np.ceil(1.0 / self.block_size))
        cells_per_block = int(self.N * self.block_size)

        for blk in range(n_blocks):
            idx_min = blk * cells_per_block
            idx_max = self.N if blk == n_blocks - 1 else (blk + 1) * cells_per_block
            idx = update_order[idx_min:idx_max]

            R_block = self._R.index_select(1, idx)
            bidx = self._batch_id.index_select(0, idx)  # (blockN,)

            # Remove cells from statistics
            self._E -= torch.outer(R_block.sum(dim=1), self._Pr_b)

            # Update O via scatter-add instead of GEMM with one-hot Phi_block
            O_block = torch.zeros((self.K, self.B), dtype=torch.float32, device=self.device)
            O_block.scatter_add_(1, bidx.unsqueeze(0).expand(self.K, -1), R_block)
            self._O -= O_block

            # Numerically stable recomputation in log-space
            # log_scale = -dist/sigma
            dist_block = self._dist_mat.index_select(1, idx)
            log_scale = -dist_block / self._sigma[:, None]

            # Dirichlet-prior KL-to-target penalty in log-space:
            # q_{k,b} = (O_{k,b} + beta * Pr_b) / sum_{b'}(...)
            # penalty(k,b) = -theta_b * (log q_{k,b} - log Pr_b)
            # This downweights overrepresented batches in cluster k and is stabilized by pseudo-counts.
            beta = self._beta
            O_smooth = torch.clamp(self._O + beta * self._Pr_b.unsqueeze(0), min=1e-8)  # (K, B)
            log_q = torch.log(O_smooth) - torch.log(O_smooth.sum(dim=1, keepdim=True))  # (K, B)
            log_Pr = torch.log(torch.clamp(self._Pr_b, min=1e-8)).unsqueeze(0)  # (1, B)
            log_penalty_kb = -(self._theta.unsqueeze(0) * (log_q - log_Pr))  # (K, B)
            log_penalty = log_penalty_kb.index_select(1, bidx)  # (K, blockN)

            logits = log_scale + log_penalty
            R_block_new = torch.softmax(logits, dim=0)

            # Put cells back
            self._E += torch.outer(R_block_new.sum(dim=1), self._Pr_b)

            O_block_new = torch.zeros((self.K, self.B), dtype=torch.float32, device=self.device)
            O_block_new.scatter_add_(1, bidx.unsqueeze(0).expand(self.K, -1), R_block_new)
            self._O += O_block_new

            # Write back in place (no full-matrix permutes/argsort)
            self._R[:, idx] = R_block_new

    def check_convergence(self, i_type):
        if i_type == 0:
            if len(self.objective_kmeans) <= self.window_size + 1:
                return False

            w = self.window_size
            obj_old = sum(self.objective_kmeans[-w-1:-1])
            obj_new = sum(self.objective_kmeans[-w:])
            return abs(obj_old - obj_new) / abs(obj_old) < self.epsilon_kmeans

        if i_type == 1:
            if len(self.objective_harmony) < 2:
                return False

            obj_old = self.objective_harmony[-2]
            obj_new = self.objective_harmony[-1]
            return (obj_old - obj_new) / abs(obj_old) < self.epsilon_harmony

        return True

    def moe_correct_ridge(self):
        """Ridge regression correction for batch effects with a trust-region (proximal) step.

        We first compute the proposed correction direction Delta (same as the original
        ridge correction), then apply a globally-scaled update Z_corr = Z_orig - eta*Delta
        where eta is chosen to satisfy a movement budget derived from tau.
        """
        # Start from original each iteration
        self._Z_corr.copy_(self._Z_orig)

        # Accumulate proposed correction direction (Delta has same shape as Z: d x N)
        Delta = torch.zeros_like(self._Z_orig)

        # Precompute for weighted sums
        batch_id = self._batch_id  # (N,)
        Zt = self._Z_orig.T.contiguous()  # (N, d)

        for k in range(self.K):
            # Compute lambda if estimating
            if self.lambda_estimation:
                lamb_vec = find_lambda_torch(self.alpha, self._E[k, :], self.device)
            else:
                lamb_vec = self._lamb

            r = self._R[k, :]  # (N,)

            # sb[b] = sum_{i in batch b} r_i
            sb = torch.zeros((self.B,), dtype=torch.float32, device=self.device)
            sb.scatter_add_(0, batch_id, r)

            # zb[b,:] = sum_{i in batch b} (r_i * z_i)
            zb = torch.zeros((self.B, self.d), dtype=torch.float32, device=self.device)
            zb.scatter_add_(0, batch_id.unsqueeze(1).expand(-1, self.d), Zt * r.unsqueeze(1))

            s0 = sb.sum()
            z0 = zb.sum(dim=0)

            # Build cov_mat directly (B+1 x B+1)
            cov_mat = torch.zeros((self.B + 1, self.B + 1), dtype=torch.float32, device=self.device)
            cov_mat[0, 0] = s0
            cov_mat[0, 1:] = sb
            cov_mat[1:, 0] = sb
            cov_mat[1:, 1:] = torch.diag(sb)
            cov_mat = cov_mat + torch.diag(lamb_vec)

            # Build RHS directly (B+1 x d)
            RHS = torch.zeros((self.B + 1, self.d), dtype=torch.float32, device=self.device)
            RHS[0, :] = z0
            RHS[1:, :] = zb

            # Solve (prefer Cholesky, fallback to solve)
            try:
                L = torch.linalg.cholesky(cov_mat)
                W = torch.cholesky_solve(RHS, L)  # (B+1, d)
            except RuntimeError:
                W = torch.linalg.solve(cov_mat, RHS)

            W[0, :] = 0  # Do not remove intercept

            # Proposed correction contribution for this cluster:
            # Delta[:, i] += r_i * W[batch_i+1, :].T
            Wb = W[1:, :]  # (B, d)
            W_cell = Wb.index_select(0, batch_id)  # (N, d)
            Delta += (W_cell.T * r.unsqueeze(0))

        # Trust-region / proximal scaling (global Frobenius movement budget)
        # Interpret self._tau_trust > 0 as a "max relative displacement":
        #   ||Z_corr - Z_orig||_F <= tau * ||Z_orig||_F
        eta = 1.0
        if self._tau_trust > 0:
            delta = self._tau_trust * torch.linalg.norm(self._Z_orig)
            denom = torch.linalg.norm(Delta).clamp_min(1e-12)
            eta = float(torch.clamp(delta / denom, max=1.0).item())

        self._Z_corr = self._Z_orig - (Delta * eta)

        # Update Z_cos (faster/stabler) and ensure contiguity
        den = torch.rsqrt((self._Z_corr * self._Z_corr).sum(dim=0, keepdim=True).clamp_min(1e-12))
        self._Z_cos = (self._Z_corr * den).contiguous()


def safe_entropy_torch(x):
    """Compute x * log(x), returning 0 where x is 0 or negative."""
    result = x * torch.log(x)
    result = torch.where(torch.isfinite(result), result, torch.zeros_like(result))
    return result


def harmony_pow_torch(A, T):
    """Element-wise power with different exponents per column (vectorized)."""
    return A.pow(T.unsqueeze(0))


def find_lambda_torch(alpha, cluster_E, device):
    """Compute dynamic lambda based on cluster expected counts."""
    lamb = torch.zeros(len(cluster_E) + 1, dtype=torch.float32, device=device)
    lamb[1:] = cluster_E * alpha
    return lamb
