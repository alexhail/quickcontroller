import { test, expect } from '@playwright/test'

const TEST_USER = {
  email: `test-${Date.now()}@example.com`,
  password: 'testpassword123',
}

test.describe('Authentication', () => {
  test.describe('Registration', () => {
    test('should show registration form', async ({ page }) => {
      await page.goto('/register')

      await expect(page.locator('h1')).toContainText('Create Account')
      await expect(page.locator('input#email')).toBeVisible()
      await expect(page.locator('input#password')).toBeVisible()
      await expect(page.locator('input#confirmPassword')).toBeVisible()
    })

    test('should show error for mismatched passwords', async ({ page }) => {
      await page.goto('/register')

      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', 'password123')
      await page.fill('input#confirmPassword', 'differentpassword')
      await page.click('button[type="submit"]')

      await expect(page.locator('.error')).toContainText('Passwords do not match')
    })

    test('should show error for short password', async ({ page }) => {
      await page.goto('/register')

      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', 'short')
      await page.fill('input#confirmPassword', 'short')
      await page.click('button[type="submit"]')

      await expect(page.locator('.error')).toContainText('at least 8 characters')
    })

    test('should successfully register new user', async ({ page }) => {
      await page.goto('/register')

      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.fill('input#confirmPassword', TEST_USER.password)
      await page.click('button[type="submit"]')

      // Should redirect to dashboard after successful registration
      await expect(page).toHaveURL('/')
      await expect(page.locator('h2')).toContainText('Welcome')
    })

    test('should show error for duplicate email', async ({ page }) => {
      await page.goto('/register')

      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.fill('input#confirmPassword', TEST_USER.password)
      await page.click('button[type="submit"]')

      await expect(page.locator('.error')).toContainText('already registered')
    })
  })

  test.describe('Login', () => {
    test('should show login form', async ({ page }) => {
      await page.goto('/login')

      await expect(page.locator('h1')).toContainText('Login')
      await expect(page.locator('input#email')).toBeVisible()
      await expect(page.locator('input#password')).toBeVisible()
    })

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/login')

      await page.fill('input#email', 'nonexistent@example.com')
      await page.fill('input#password', 'wrongpassword')
      await page.click('button[type="submit"]')

      await expect(page.locator('.error')).toContainText('Invalid email or password')
    })

    test('should successfully login with valid credentials', async ({ page }) => {
      await page.goto('/login')

      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.click('button[type="submit"]')

      // Should redirect to dashboard
      await expect(page).toHaveURL('/')
      await expect(page.locator('.email')).toContainText(TEST_USER.email)
    })

    test('should navigate to register page', async ({ page }) => {
      await page.goto('/login')

      await page.click('a[href="/register"]')

      await expect(page).toHaveURL('/register')
    })
  })

  test.describe('Protected Routes', () => {
    test('should redirect to login when accessing dashboard without auth', async ({ page }) => {
      // Clear any existing session
      await page.context().clearCookies()

      await page.goto('/')

      await expect(page).toHaveURL('/login')
    })

    test('should redirect to dashboard when accessing login while authenticated', async ({ page }) => {
      // Login first
      await page.goto('/login')
      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.click('button[type="submit"]')
      await expect(page).toHaveURL('/')

      // Try to access login page
      await page.goto('/login')

      // Should redirect back to dashboard
      await expect(page).toHaveURL('/')
    })
  })

  test.describe('Logout', () => {
    test('should successfully logout', async ({ page }) => {
      // Login first
      await page.goto('/login')
      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.click('button[type="submit"]')
      await expect(page).toHaveURL('/')

      // Logout
      await page.click('.logout-btn')

      // Should redirect to login
      await expect(page).toHaveURL('/login')
    })

    test('should not access dashboard after logout', async ({ page }) => {
      // Login
      await page.goto('/login')
      await page.fill('input#email', TEST_USER.email)
      await page.fill('input#password', TEST_USER.password)
      await page.click('button[type="submit"]')
      await expect(page).toHaveURL('/')

      // Logout
      await page.click('.logout-btn')
      await expect(page).toHaveURL('/login')

      // Try to access dashboard
      await page.goto('/')
      await expect(page).toHaveURL('/login')
    })
  })
})
