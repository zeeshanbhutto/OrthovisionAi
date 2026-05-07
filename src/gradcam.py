import torch


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer

        self.gradients = None
        self.activations = None

        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        self.target_layer.register_forward_hook(forward_hook)

        try:
            self.target_layer.register_full_backward_hook(backward_hook)
        except Exception:
            self.target_layer.register_backward_hook(backward_hook)

    def generate(self, input_image, class_idx):
        self.model.eval()

        output = self.model(input_image)

        self.model.zero_grad()
        output[0, class_idx].backward()

        gradients = self.gradients[0]
        activations = self.activations[0]

        weights = torch.mean(gradients, dim=(1, 2))

        cam = torch.zeros(
            activations.shape[1:],
            dtype=torch.float32,
            device=activations.device
        )

        for i, weight in enumerate(weights):
            cam += weight * activations[i]

        cam = torch.relu(cam)
        cam = cam - cam.min()

        max_value = cam.max()
        if max_value > 0:
            cam = cam / max_value

        return cam.detach().cpu().numpy()