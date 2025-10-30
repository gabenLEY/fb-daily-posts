/**
 * Frontend utility for async image generation
 * Handles Heroku timeout issues
 */

class AsyncImageGenerator {
  constructor(apiBaseUrl) {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Generate image with automatic fallback to async if sync fails
   */
  async generateImage(prompt, size = "1024x1024", maxWaitTime = 25000) {
    try {
      // First try sync generation (faster if it works)
      console.log("🎨 Trying sync image generation...");
      return await this.generateImageSync(prompt, size, maxWaitTime);
    } catch (error) {
      console.warn(
        "⚠️ Sync generation failed, falling back to async:",
        error.message
      );

      // Fall back to async generation
      return await this.generateImageAsync(prompt, size);
    }
  }

  /**
   * Sync image generation with timeout
   */
  async generateImageSync(prompt, size = "1024x1024", timeout = 25000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/social/generate-image`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt, size }),
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return result.data;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Async image generation with polling
   */
  async generateImageAsync(prompt, size = "1024x1024") {
    console.log("🔄 Starting async image generation...");

    // Start the job
    const startResponse = await fetch(
      `${this.apiBaseUrl}/api/social/generate-image-async`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt, size }),
      }
    );

    if (!startResponse.ok) {
      throw new Error(`Failed to start job: ${startResponse.statusText}`);
    }

    const { job_id } = await startResponse.json();
    console.log(`✅ Job started: ${job_id}`);

    // Poll for result
    return await this.pollJobResult(job_id);
  }

  /**
   * Poll job status until completion
   */
  async pollJobResult(jobId, maxAttempts = 60, pollInterval = 2000) {
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await fetch(
          `${this.apiBaseUrl}/api/social/job-status/${jobId}`
        );

        if (!response.ok) {
          throw new Error(`Failed to get job status: ${response.statusText}`);
        }

        const job = await response.json();
        console.log(`📊 Job ${jobId} status: ${job.status}`);

        switch (job.status) {
          case "completed":
            console.log("✅ Image generation completed!");
            return job.result;

          case "failed":
            throw new Error(`Job failed: ${job.error}`);

          case "processing":
          case "pending":
            // Continue polling
            break;

          default:
            console.warn(`Unknown job status: ${job.status}`);
        }

        // Wait before next poll
        await new Promise((resolve) => setTimeout(resolve, pollInterval));
        attempts++;
      } catch (error) {
        console.error(`Error polling job ${jobId}:`, error);
        attempts++;

        if (attempts >= maxAttempts) {
          throw new Error(`Job polling timeout after ${maxAttempts} attempts`);
        }

        // Wait before retry
        await new Promise((resolve) => setTimeout(resolve, pollInterval));
      }
    }

    throw new Error("Job polling timeout");
  }
}

// Usage example:
/*
const imageGenerator = new AsyncImageGenerator('https://randevoupost.cloud');

// Use it in your app
async function handleImageGeneration() {
    try {
        showLoadingSpinner('🎨 Generating image...');
        
        const result = await imageGenerator.generateImage(
            'A beautiful sunset over mountains',
            '1024x1024'
        );
        
        console.log('Generated image:', result);
        displayImage(result.image_url || result.image_data);
        
    } catch (error) {
        console.error('Image generation failed:', error);
        showError('Failed to generate image. Please try again.');
    } finally {
        hideLoadingSpinner();
    }
}
*/

export default AsyncImageGenerator;
