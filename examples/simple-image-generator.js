/**
 * Simple Image Generation Helper
 * Automatically handles timeouts by falling back to async generation
 */

// Simple utility for your frontend
window.ImageGenerator = {
  baseUrl: "https://randevoupost.cloud",

  async generateImage(prompt, size = "1024x1024") {
    try {
      console.log("🎨 Starting image generation...");

      // Try sync first (faster if it works)
      const response = await fetch(
        `${this.baseUrl}/api/social/generate-image`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt, size }),
        }
      );

      const result = await response.json();

      if (response.ok) {
        if (result.warning) {
          console.warn("⚠️ Got placeholder due to timeout:", result.warning);
        }
        return result.data;
      }

      // If sync failed with timeout, try async
      if (response.status === 408 || result.error?.includes("timeout")) {
        console.log("🔄 Sync timed out, trying async...");
        return await this.generateImageAsync(prompt, size);
      }

      throw new Error(result.error || "Generation failed");
    } catch (error) {
      console.error("❌ Sync generation failed:", error.message);

      // Fallback to async if sync completely fails
      console.log("🔄 Falling back to async generation...");
      return await this.generateImageAsync(prompt, size);
    }
  },

  async generateImageAsync(prompt, size = "1024x1024") {
    try {
      // Start async job
      const startResponse = await fetch(
        `${this.baseUrl}/api/social/generate-image-async`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt, size }),
        }
      );

      if (!startResponse.ok) {
        const error = await startResponse.json();
        throw new Error(error.error || "Failed to start generation");
      }

      const { job_id } = await startResponse.json();
      console.log(`✅ Job started: ${job_id}`);

      // Poll for result
      return await this.pollJobResult(job_id);
    } catch (error) {
      console.error("❌ Async generation failed:", error.message);
      throw error;
    }
  },

  async pollJobResult(jobId, maxAttempts = 30) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(
          `${this.baseUrl}/api/social/job-status/${jobId}`
        );
        const job = await response.json();

        console.log(
          `📊 Job ${jobId} status: ${job.status} (${
            attempt + 1
          }/${maxAttempts})`
        );

        switch (job.status) {
          case "completed":
            console.log("✅ Image generation completed!");
            return job.result;

          case "failed":
            throw new Error(`Job failed: ${job.error}`);

          case "processing":
          case "pending":
            // Wait and continue polling
            await new Promise((resolve) => setTimeout(resolve, 2000));
            break;

          default:
            console.warn(`Unknown status: ${job.status}`);
        }
      } catch (error) {
        console.error(`Error polling job ${jobId}:`, error);
        if (attempt === maxAttempts - 1) throw error;
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }

    throw new Error("Job polling timeout");
  },
};

// Usage example for your existing code:
/*
// Replace your current image generation call with:
try {
    showLoading('Generating image...');
    const result = await ImageGenerator.generateImage(prompt, size);
    
    // Use result.image_url or result.b64_image
    displayImage(result.image_url || result.b64_image);
    
} catch (error) {
    console.error('Image generation failed:', error);
    showError('Failed to generate image. Please try again.');
} finally {
    hideLoading();
}
*/
