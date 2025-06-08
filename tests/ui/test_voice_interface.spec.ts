import { test, expect } from '@playwright/test';

// Global test configuration
test.describe.configure({ mode: 'parallel' });

// Test configuration
test.use({
  baseURL: 'http://localhost:8000',
  viewport: { width: 1920, height: 1080 }
});

// Test suite
test.describe('Voice Agent Interface', () => {
  test('basic functionality', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test language selection
    await test.step('language selection', async () => {
      const languageSelector = page.locator('select#language-picker');
      await languageSelector.selectOption('fr-FR');
      expect(await languageSelector.inputValue()).toBe('fr-FR');
    });

    // Test microphone interaction
    await test.step('microphone interaction', async () => {
      const micButton = page.locator('button#mic');
      await micButton.click();
      await page.waitForSelector('.waveform-active');
    });

    // Test text input
    await test.step('text input', async () => {
      const input = page.locator('input#text-input');
      await input.fill('Bonjour, qui êtes-vous?');
      await expect(input).toHaveValue('Bonjour, qui êtes-vous?');
    });

    // Test submit
    await test.step('submit interaction', async () => {
      const submitButton = page.locator('button#submit');
      await submitButton.click();
      await expect(page.locator('.agent-response')).toContainText('Bonjour');
    });
  });

  test('emotion visualization', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test emotion display
    await test.step('emotion display', async () => {
      const emotionPanel = page.locator('.emotion-panel');
      await expect(emotionPanel).toBeVisible();

      // Test emotion bars
      const emotionBars = emotionPanel.locator('.emotion-bar');
      await expect(emotionBars).toHaveCount(7); // 7 emotions

      // Test emotion icons
      const emotionIcons = emotionPanel.locator('.emotion-icon');
      await expect(emotionIcons).toHaveCount(7);
    });

    // Test emotion interaction
    await test.step('emotion interaction', async () => {
      const emotionItem = page.locator('.emotion-item').first();
      await emotionItem.click();
      await expect(emotionItem).toHaveClass(/active/);
    });
  });

  test('error handling', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test error display
    await test.step('error display', async () => {
      const errorButton = page.locator('button#error-test');
      await errorButton.click();
      await expect(page.locator('.error-toast')).toBeVisible();
    });

    // Test error recovery
    await test.step('error recovery', async () => {
      const retryButton = page.locator('button#retry');
      await retryButton.click();
      await expect(page.locator('.error-toast')).toBeHidden();
    });
  });

  test('loading states', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test loading indicators
    await test.step('loading indicators', async () => {
      const loadingButton = page.locator('button#loading-test');
      await loadingButton.click();
      await expect(page.locator('.loading-indicator')).toBeVisible();
    });

    // Test loading completion
    await test.step('loading completion', async () => {
      await page.waitForTimeout(2000); // Simulate API response
      await expect(page.locator('.loading-indicator')).toBeHidden();
    });
  });

  test('multilingual support', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test multiple languages
    const languages = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'it-IT'];
    
    for (const lang of languages) {
      await test.step(`test language ${lang}`, async () => {
        const languageSelector = page.locator('select#language-picker');
        await languageSelector.selectOption(lang);
        await expect(languageSelector.inputValue()).toBe(lang);
      });
    }
  });

  test('performance', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test response time
    await test.step('response time', async () => {
      const startTime = Date.now();
      await page.locator('button#test-response').click();
      await page.locator('.agent-response').waitFor({ 
        state: 'visible',
        timeout: 5000 
      });
      const duration = Date.now() - startTime;
      console.log(`Response time: ${duration}ms`);
      expect(duration).toBeLessThan(5000);
    });

    // Test concurrent requests
    await test.step('concurrent requests', async () => {
      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(
          page.locator(`button#test-response-${i}`).click()
        );
      }
      await Promise.all(promises);
    });
  });

  test('accessibility', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test keyboard navigation
    await test.step('keyboard navigation', async () => {
      await page.keyboard.press('Tab');
      await expect(page.locator('button#mic')).toBeFocused();
    });

    // Test screen reader support
    await test.step('screen reader support', async () => {
      const ariaLabels = page.locator('[aria-label]');
      await expect(ariaLabels).toHaveCount(10);
    });
  });
});

// Test suite
test.describe('Voice Agent Interface', () => {
  test('basic functionality', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test language selection
    await test.step('language selection', async () => {
      const languageSelector = page.locator('select#language-picker');
      await languageSelector.selectOption('fr-FR');
      expect(await languageSelector.inputValue()).toBe('fr-FR');
    });

    // Test microphone interaction
    await test.step('microphone interaction', async () => {
      const micButton = page.locator('button#mic');
      await micButton.click();
      await page.waitForSelector('.waveform-active');
    });

    // Test text input
    await test.step('text input', async () => {
      const input = page.locator('input#text-input');
      await input.fill('Bonjour, qui êtes-vous?');
      await expect(input).toHaveValue('Bonjour, qui êtes-vous?');
    });

    // Test submit
    await test.step('submit interaction', async () => {
      const submitButton = page.locator('button#submit');
      await submitButton.click();
      await expect(page.locator('.agent-response')).toContainText('Bonjour');
    });
  });

  test('emotion visualization', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test emotion display
    await test.step('emotion display', async () => {
      const emotionPanel = page.locator('.emotion-panel');
      await expect(emotionPanel).toBeVisible();

      // Test emotion bars
      const emotionBars = emotionPanel.locator('.emotion-bar');
      await expect(emotionBars).toHaveCount(7); // 7 emotions

      // Test emotion icons
      const emotionIcons = emotionPanel.locator('.emotion-icon');
      await expect(emotionIcons).toHaveCount(7);
    });

    // Test emotion interaction
    await test.step('emotion interaction', async () => {
      const emotionItem = page.locator('.emotion-item').first();
      await emotionItem.click();
      await expect(emotionItem).toHaveClass(/active/);
    });
  });

  test('error handling', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test error display
    await test.step('error display', async () => {
      const errorButton = page.locator('button#error-test');
      await errorButton.click();
      await expect(page.locator('.error-toast')).toBeVisible();
    });

    // Test error recovery
    await test.step('error recovery', async () => {
      const retryButton = page.locator('button#retry');
      await retryButton.click();
      await expect(page.locator('.error-toast')).toBeHidden();
    });
  });

  test('loading states', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test loading indicators
    await test.step('loading indicators', async () => {
      const loadingButton = page.locator('button#loading-test');
      await loadingButton.click();
      await expect(page.locator('.loading-indicator')).toBeVisible();
    });

    // Test loading completion
    await test.step('loading completion', async () => {
      await page.waitForTimeout(2000); // Simulate API response
      await expect(page.locator('.loading-indicator')).toBeHidden();
    });
  });

  test('multilingual support', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test multiple languages
    const languages = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'it-IT'];
    
    for (const lang of languages) {
      await test.step(`test language ${lang}`, async () => {
        const languageSelector = page.locator('select#language-picker');
        await languageSelector.selectOption(lang);
        await expect(languageSelector.inputValue()).toBe(lang);
      });
    }
  });

  test('performance', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test response time
    await test.step('response time', async () => {
      const startTime = Date.now();
      await page.locator('button#test-response').click();
      await page.locator('.agent-response').waitFor({ 
        state: 'visible',
        timeout: 5000 
      });
      const duration = Date.now() - startTime;
      console.log(`Response time: ${duration}ms`);
      expect(duration).toBeLessThan(5000);
    });

    // Test concurrent requests
    await test.step('concurrent requests', async () => {
      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(
          page.locator(`button#test-response-${i}`).click()
        );
      }
      await Promise.all(promises);
    });
  });

  test('accessibility', async ({ page }) => {
    await page.goto('/voice-agent');
    
    // Test keyboard navigation
    await test.step('keyboard navigation', async () => {
      await page.keyboard.press('Tab');
      await expect(page.locator('button#mic')).toBeFocused();
    });

    // Test screen reader support
    await test.step('screen reader support', async () => {
      const ariaLabels = page.locator('[aria-label]');
      await expect(ariaLabels).toHaveCount(10);
    });
  });
});
